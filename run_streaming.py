"""Run the full streaming pipeline with MLFlow tracking."""

from data_simulation.generator import generate_grid_data
from data_simulation.stream import stream_data
from pipeline.forecasting_pipeline import ForecastPipeline
from models.registry import register_best_model

def main():
    """Run streaming experiment with drift detection."""
    print("Starting streaming experiment with drift detection...")
    
    # Generate data
    data = generate_grid_data()
    stream = stream_data(data)
    
    # Run pipeline
    pipeline = ForecastPipeline()
    pipeline.run(stream)
    
    print("✅ Streaming completed!")
    print(f"📊 Total steps: {pipeline.step}")
    print(f"🔄 Retrains: {pipeline.version}")
    
    # Register best model
    print("\n📦 Registering best model...")
    register_best_model(
        experiment_name="TimeSeries-Development",
        model_name="TimeSeries-GradientBoosting"
    )
    
    print("✅ Done!")
    print("📊 Check MLFlow UI: http://localhost:5000")

if __name__ == "__main__":
    main()
