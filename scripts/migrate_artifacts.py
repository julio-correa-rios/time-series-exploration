"""
One-shot migration:
  1) Move legacy artifact tree ./mlruns/artifacts/ -> ./mlartifacts/
  2) Rewrite all metadata files (yaml/json) so artifact_uri / artifact_location /
     artifact_path point at the new location.
  3) Mark stale RUNNING runs (status=1 with end_time=null) as KILLED (status=5).

Idempotent: safe to re-run. Run after stopping the MLflow server.

    python scripts/migrate_artifacts.py
"""

import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MLRUNS = ROOT / "mlruns"
OLD_ART = MLRUNS / "artifacts"
NEW_ART = ROOT / "mlartifacts"
LEGACY_BACKUP = ROOT / "mlruns_artifacts_legacy_backup"

OLD_ABS = str(OLD_ART)
NEW_ABS = str(NEW_ART)
OLD_REL = "mlruns/artifacts"
NEW_REL = "mlartifacts"

REWRITE_EXTS = {".yaml", ".yml", ".json"}


def _rewrite_in_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    new_text = text.replace(OLD_ABS, NEW_ABS).replace(OLD_REL, NEW_REL)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def rewrite_paths_under(root: Path) -> int:
    if not root.exists():
        return 0
    count = 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in REWRITE_EXTS:
            if _rewrite_in_file(p):
                count += 1
    return count


def _merge_into(src: Path, dst: Path) -> None:
    """Move src into dst, merging directory trees and overwriting nothing existing."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.iterdir()):
        target = dst / item.name
        if target.exists():
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
                shutil.rmtree(item)
            else:
                if not target.exists():
                    shutil.copy2(item, target)
                item.unlink()
        else:
            shutil.move(str(item), str(target))
    try:
        src.rmdir()
    except OSError:
        pass


def move_artifact_dir() -> bool:
    if not OLD_ART.exists():
        return False
    _merge_into(OLD_ART, NEW_ART)
    return True


def fold_legacy_backup() -> bool:
    if not LEGACY_BACKUP.exists():
        return False
    _merge_into(LEGACY_BACKUP, NEW_ART)
    return True


def fix_stale_running_runs(exp_root: Path) -> int:
    """Mark RUNNING (status=1, end_time null) runs as KILLED (status=5)."""
    if not exp_root.exists():
        return 0
    changed = 0
    for run_dir in exp_root.iterdir():
        if not run_dir.is_dir():
            continue
        meta_path = run_dir / "meta.yaml"
        if not meta_path.exists():
            continue
        with meta_path.open("r", encoding="utf-8") as f:
            meta = yaml.safe_load(f)
        if not isinstance(meta, dict):
            continue
        status = meta.get("status")
        end_time = meta.get("end_time")
        if status == 1 and end_time in (None, "null"):
            start = int(meta.get("start_time") or 0)
            meta["status"] = 5
            meta["end_time"] = start + 60_000  # +1 min, harmless placeholder
            with meta_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(meta, f, sort_keys=False)
            print(f"    KILLED: {run_dir.name} (was RUNNING)")
            changed += 1
    return changed


def main() -> None:
    print(f"Source (legacy):  {OLD_ART}")
    print(f"Target:           {NEW_ART}")

    print("\n[1/5] Moving fresh artifact tree (mlruns/artifacts -> mlartifacts)...")
    moved = move_artifact_dir()
    print("  done" if moved else "  nothing to move")

    print("\n[2/5] Folding legacy backup into mlartifacts...")
    folded = fold_legacy_backup()
    print("  done" if folded else "  no legacy backup found")

    print("\n[3/5] Rewriting paths in backend store (./mlruns)...")
    n_mlruns = rewrite_paths_under(MLRUNS)
    print(f"  rewrote {n_mlruns} file(s)")

    print("\n[4/5] Rewriting paths in new artifact tree (./mlartifacts)...")
    n_mlart = rewrite_paths_under(NEW_ART)
    print(f"  rewrote {n_mlart} file(s)")

    print("\n[5/5] Marking stale RUNNING runs as KILLED...")
    fixed = 0
    if MLRUNS.exists():
        for exp_dir in MLRUNS.iterdir():
            if exp_dir.is_dir() and exp_dir.name.isdigit():
                fixed += fix_stale_running_runs(exp_dir)
    print(f"  fixed {fixed} run(s)")

    print("\nMigration complete.")


if __name__ == "__main__":
    main()
