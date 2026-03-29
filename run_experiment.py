"""Script to run a training experiment with MLFlow tracking."""

import pandas as pd
from data_simulation.generator import generate_grid_data
from models.training import train_model

def main():
    """Run a single training experiment."""
    print("🚀 Starting training experiment...")
    
    # Generate data
    data = generate_grid_data()
    
    # Train model with MLFlow tracking
    model = train_model(data, run_name="experiment_001")
    
    print("✅ Training completed!")
    print("📊 Check MLFlow UI at http://localhost:5000")

if __name__ == "__main__":
    main()