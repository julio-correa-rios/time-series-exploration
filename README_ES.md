# Time Series Analysis - Pipeline ML

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un pipeline completo de machine learning para análisis y pronóstico de series de tiempo con integración de **MLFlow**, detección de drift y monitoreo en tiempo real.

📖 **[Read in English](README.md)**

## 📋 Características

- ✅ **Generación de datos simulados** con patrones realistas de series de tiempo
- ✅ **Feature engineering** automático con pipeline configurable
- ✅ **Entrenamiento y predicción** con modelos de ensemble (Gradient Boosting)
- ✅ **Tracking experimental** completo con MLFlow
- ✅ **Detección de drift** en datos para monitoreo de calidad
- ✅ **Registro de modelos** con versionado semántico
- ✅ **Predicción en streaming** en tiempo real
- ✅ **Configuración centralizada** y flexible

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.9 o superior
- pip o conda

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/time-series-analysis.git
cd time-series-analysis
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -e .
```

Para desarrollo (con testing):
```bash
pip install -e ".[dev]"
```

Con soporte para Airflow:
```bash
pip install -e ".[airflow, aws]"
```

## 📁 Estructura del Proyecto

```
time_series_analysis/
├── config/                      # Configuración centralizada
│   ├── settings.py             # Variables de entorno y configuración
│   └── __init__.py
├── data_simulation/            # Generación de datos sintéticos
│   ├── generator.py            # Generador de grid de datos
│   ├── stream.py               # Streaming en tiempo real
│   └── __init__.py
├── features/                   # Feature engineering
│   ├── pipeline.py             # Pipeline de transformaciones
│   ├── transformations.py      # Transformaciones individuales
│   ├── registry.py             # Registro de features
│   └── __init__.py
├── models/                     # Modelos de ML
│   ├── training.py             # Entrenamiento con MLFlow
│   ├── inference.py            # Predicciones
│   ├── registry.py             # Registro y gestión de modelos
│   └── __init__.py
├── pipeline/                   # Pipeline principal
│   ├── forecasting_pipeline.py # Orquestación del pipeline
│   └── __init__.py
├── monitoring/                 # Monitoreo y detección de anomalías
│   ├── drift.py                # Detección de Data Drift
│   └── __init__.py
├── mlflow_integration/         # Integración MLFlow
│   ├── config.py               # Configuración MLFlow
│   ├── tracking.py             # Funciones de tracking
│   └── __init__.py
├── main.py                     # Script principal
├── run_experiment.py           # Ejecutar experimentos
├── run_streaming.py            # Ejecutar en modo streaming
├── pyproject.toml              # Configuración del proyecto
└── README_ES.md                # Este archivo
```

## 🔧 Uso

### Ejecutar pipeline completo

```bash
python main.py
```

### Ejecutar experimentos

```bash
python run_experiment.py
```

### Modo streaming en tiempo real

```bash
python run_streaming.py
```

## ⚙️ Configuración

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# MLFlow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=TimeSeries-Development

# Configuración de datos
BUFFER_SIZE=100
WINDOW_SIZE=24
FORECAST_HORIZON=12

# AWS (opcional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

### Archivos de Configuración

Ver [config/settings.py](config/settings.py) para todas las opciones configurables.

## 📊 MLFlow

### Iniciar MLFlow Server

```bash
mlflow server --host 0.0.0.0 --port 5000
```

Luego accede a `http://localhost:5000` en tu navegador.

### Características Tracked

- **Parámetros**: Tamaño de ventana, horizonte de pronóstico
- **Métricas**: MAE, RMSE, MAPE, conteo de reentrenamientos
- **Modelos**: Modelos GradientBoosting registrados
- **Artefactos**: Gráficos, datos de validación, reportes

## 🔍 Detección de Drift

El pipeline monitorea automáticamente:
- Cambios en la distribución de datos
- Variación en estadísticas clave
- Correlaciones anómalas

Cuando se detecta drift, se dispara un reentrenamiento automático.

## 📦 Dependencias Principales

- **pandas** (1.3.0+): Manipulación de datos
- **scikit-learn** (1.0.0+): Modelos y métricas
- **numpy** (1.20.0+): Computación numérica
- **mlflow** (2.0.0+): Experimentación y tracking
- **python-dotenv** (0.19.0+): Gestión de variables de entorno

## 🧪 Testing

Ejecutar tests:
```bash
pytest
```

Con cobertura:
```bash
pytest --cov=. --cov-report=html
```

Linting:
```bash
flake8 .
```

Formato de código:
```bash
black .
```

## 📈 Flujo de Trabajo Típico

1. **Generación de datos** → Datos sintéticos realistas
2. **Feature Engineering** → Transformaciones automáticas
3. **Entrenamiento** → Model fitting con MLFlow tracking
4. **Validación** → Evaluación en datos test
5. **Monitoreo** → Detección de drift en producción
6. **Reentrenamiento** → Automático si se detecta drift
7. **Predicción** → Inferencia en streaming

## 📚 Documentación Adicional

- [Feature Pipeline](features/README.md) - Detalles de transformaciones
- [Monitoring](monitoring/README.md) - Detección de anomalías
- [MLFlow Integration](mlflow_integration/README.md) - Tracking avanzado

## 🚦 Estado del Proyecto

- [x] Pipeline base funcional
- [x] Integración MLFlow completa
- [x] Detección de drift
- [x] Predicción en streaming
- [ ] Integración Airflow
- [ ] Deploy en AWS
- [ ] API REST para predicciones

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para cambios significativos:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estilo de Código

- Seguir PEP 8
- Usar `black` para formateo
- Incluir docstrings en funciones
- Mantener cobertura de tests > 80%

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Julio Correo Arios**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [tu-linkedin](https://linkedin.com/in/tu-linkedin)

## 📧 Contacto

Para preguntas o sugerencias, contactar a: tu-email@example.com

## 🙏 Agradecimientos

- Comunidad Python
- MLFlow team
- Scikit-learn contributors

---

**Última actualización**: Marzo 2026
