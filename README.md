# Time Series Analysis - ML Pipeline

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive machine learning pipeline for time series analysis and forecasting with **MLFlow** integration, drift detection, and real-time monitoring.

📖 **[Lee en español](README_ES.md)**

## 📋 Features

- ✅ **Synthetic Data Generation** with realistic time series patterns
- ✅ **Automated Feature Engineering** with configurable pipelines
- ✅ **Training & Prediction** with ensemble models (Gradient Boosting)
- ✅ **Complete MLFlow Tracking** for experiments
- ✅ **Data Drift Detection** for quality monitoring
- ✅ **Model Registry** with semantic versioning
- ✅ **Real-time Streaming Prediction**
- ✅ **Centralized & Flexible Configuration**

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip or conda

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/time-series-analysis.git
cd time-series-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -e .
```

For development (with testing):
```bash
pip install -e ".[dev]"
```

With Airflow support:
```bash
pip install -e ".[airflow, aws]"
```

## 📁 Project Structure

```
time_series_analysis/
├── config/                      # Centralized configuration
│   ├── settings.py             # Environment variables & config
│   └── __init__.py
├── data_simulation/            # Synthetic data generation
│   ├── generator.py            # Data grid generator
│   ├── stream.py               # Real-time streaming
│   └── __init__.py
├── features/                   # Feature engineering
│   ├── pipeline.py             # Transformation pipeline
│   ├── transformations.py      # Individual transformations
│   ├── registry.py             # Features registry
│   └── __init__.py
├── models/                     # ML Models
│   ├── training.py             # Training with MLFlow
│   ├── inference.py            # Predictions
│   ├── registry.py             # Model management & registry
│   └── __init__.py
├── pipeline/                   # Main pipeline
│   ├── forecasting_pipeline.py # Pipeline orchestration
│   └── __init__.py
├── monitoring/                 # Monitoring & anomalies
│   ├── drift.py                # Data Drift detection
│   └── __init__.py
├── mlflow_integration/         # MLFlow integration
│   ├── config.py               # MLFlow configuration
│   ├── tracking.py             # Tracking functions
│   └── __init__.py
├── main.py                     # Main entry point
├── run_experiment.py           # Run experiments
├── run_streaming.py            # Run in streaming mode
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🔧 Usage

### Run complete pipeline

```bash
python main.py
```

### Run experiments

```bash
python run_experiment.py
```

### Real-time streaming mode

```bash
python run_streaming.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# MLFlow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=TimeSeries-Development

# Data configuration
BUFFER_SIZE=100
WINDOW_SIZE=24
FORECAST_HORIZON=12

# AWS (optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

### Configuration Files

See [config/settings.py](config/settings.py) for all configurable options.

## 📊 MLFlow

### Start MLFlow Server

```bash
mlflow server --host 0.0.0.0 --port 5000
```

Then access `http://localhost:5000` in your browser.

### Tracked Features

- **Parameters**: Window size, forecast horizon
- **Metrics**: MAE, RMSE, MAPE, retrain count
- **Models**: Registered GradientBoosting models
- **Artifacts**: Plots, validation data, reports

## 🔍 Drift Detection

The pipeline automatically monitors:
- Changes in data distribution
- Variation in key statistics
- Anomalous correlations

When drift is detected, automatic retraining is triggered.

## 📦 Main Dependencies

- **pandas** (1.3.0+): Data manipulation
- **scikit-learn** (1.0.0+): Models and metrics
- **numpy** (1.20.0+): Numerical computing
- **mlflow** (2.0.0+): Experimentation and tracking
- **python-dotenv** (0.19.0+): Environment variables management

## 🧪 Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=. --cov-report=html
```

Linting:
```bash
flake8 .
```

Code formatting:
```bash
black .
```

## 📈 Typical Workflow

1. **Data Generation** → Realistic synthetic data
2. **Feature Engineering** → Automatic transformations
3. **Training** → Model fitting with MLFlow tracking
4. **Validation** → Evaluation on test data
5. **Monitoring** → Drift detection in production
6. **Retraining** → Automatic if drift detected
7. **Prediction** → Real-time streaming inference

## 📚 Additional Documentation

- [Feature Pipeline](features/README.md) - Transformation details
- [Monitoring](monitoring/README.md) - Anomaly detection
- [MLFlow Integration](mlflow_integration/README.md) - Advanced tracking

## 🚦 Project Status

- [x] Base functional pipeline
- [x] MLFlow integration
- [x] Drift detection
- [x] Streaming prediction
- [ ] Airflow integration
- [ ] AWS deployment
- [ ] REST API for predictions

## 🤝 Contributing

Contributions are welcome. For significant changes:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use `black` for formatting
- Include docstrings in functions
- Keep test coverage > 80%

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👤 Author

**Julio Correa Ríos**

- GitHub: [@julio-correa-rios](https://github.com/julio-correa-rios)
- LinkedIn: [julio-correa-rios](https://www.linkedin.com/in/juliocorrearios/)

## 📧 Contact

For questions or suggestions, contact: julio.correa.rios@gmail.com

---

**Last updated**: March 2026
