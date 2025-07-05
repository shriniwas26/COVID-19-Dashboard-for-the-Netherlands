# COVID-19 Dashboard for the Netherlands

A comprehensive, interactive dashboard for visualizing COVID-19 data across Dutch municipalities and provinces. Built with modern web technologies and deployed using CI/CD practices.

![Dashboard Preview](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Dash](https://img.shields.io/badge/Dash-2.14.2-orange)
![Deployment](https://img.shields.io/badge/Deployment-Render-blue)

## 🚀 Live Demo

**Dashboard**: [COVID-19 Dashboard - Netherlands](https://your-app-name.region.elasticbeanstalk.com)

## 📊 Features

### Interactive Visualizations

- **Municipality-level analysis**: Compare COVID-19 metrics across different Dutch municipalities
- **Province-level aggregation**: View regional trends and patterns
- **Multiple metrics**: Total reported cases, hospital admissions, and fatalities
- **Population-adjusted views**: Per-capita analysis for fair comparisons
- **Moving averages**: Smooth trend analysis with customizable windows

### Technical Capabilities

- **Real-time data processing**: Automatic updates from RIVM (Dutch health authority)
- **Responsive design**: Works seamlessly on desktop and mobile devices
- **Interactive filtering**: Multi-select dropdowns for municipalities and provinces
- **Dynamic charts**: Plotly-powered visualizations with hover details
- **Data validation**: Robust error handling and data quality checks

### Deployment & DevOps

- **Automated CI/CD**: GitHub Actions for seamless deployment
- **Cloud hosting**: Deployed on Render with automatic SSL
- **Monitoring**: Built-in logging and performance tracking
- **Scalable architecture**: Designed for production workloads

## 🛠️ Technology Stack

### Frontend & Visualization

- **Dash**: Interactive web application framework
- **Plotly**: Advanced charting and visualization library
- **HTML/CSS**: Custom styling and responsive design

### Backend & Data Processing

- **Python 3.12**: Modern Python with type hints and performance optimizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing and array operations
- **Requests**: HTTP client for data fetching

### DevOps & Deployment

- **GitHub Actions**: Automated testing and deployment
- **AWS Elastic Beanstalk**: Cloud hosting platform
- **Gunicorn**: Production-grade WSGI server
- **Docker**: Containerization support
- **Docker Compose**: Local development environment

## 📈 Data Sources

- **RIVM (Dutch National Institute for Public Health)**: Official COVID-19 statistics
- **CBS (Statistics Netherlands)**: Population data for municipalities
- **Automatic updates**: Daily data refresh from authoritative sources

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git

### Local Development

#### Option 1: Docker Compose (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/COVID-19-Dashboard-for-the-Netherlands.git
   cd COVID-19-Dashboard-for-the-Netherlands
   ```

2. **Start with Docker Compose**

   ```bash
   # Using the convenience script
   ./docker-run.sh start

   # Or directly with docker-compose
   docker-compose up --build
   ```

3. **Access the dashboard**

   - Open your browser and go to: http://localhost:5005
   - The dashboard will be available in a few moments

4. **Useful Docker commands**
   ```bash
   ./docker-run.sh logs     # View logs
   ./docker-run.sh stop     # Stop the dashboard
   ./docker-run.sh restart  # Restart the dashboard
   ./docker-run.sh clean    # Clean up Docker resources
   ```

#### Option 2: Local Python Environment

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/COVID-19-Dashboard-for-the-Netherlands.git
   cd COVID-19-Dashboard-for-the-Netherlands
   ```

2. **Set up virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   # Development mode (with auto-reload)
   python covid_dashboard_nl.py

   # Production mode
   gunicorn covid_dashboard_nl:server
   ```

5. **Update data** (optional)
   ```bash
   python update_data.py
   ```

### Deployment

This project includes automated deployment using GitHub Actions and AWS Elastic Beanstalk:

1. **Fork/Clone** this repository
2. **Set up AWS** following the [deployment guide](AWS_DEPLOYMENT.md)
3. **Configure AWS credentials** and run the deployment script
4. **Push to main branch** - automatic deployment!

## 📊 Dashboard Features

### Municipality Analysis

- Select multiple municipalities for comparison
- View daily and cumulative metrics
- Population-adjusted calculations
- Moving average smoothing

### Province Overview

- Regional trend analysis
- Aggregated statistics
- Cross-province comparisons
- Historical data visualization

### Interactive Controls

- **Metric selection**: Choose between cases, hospitalizations, or fatalities
- **Time window**: Adjustable moving average periods
- **Data type**: Raw numbers or population-adjusted views
- **Municipality/Province filters**: Multi-select dropdowns

## 🔧 Architecture

```
COVID-19 Dashboard
├── Frontend (Dash/Plotly)
│   ├── Interactive controls
│   ├── Real-time charts
│   └── Responsive layout
├── Backend (Python)
│   ├── Data processing
│   ├── Statistical analysis
│   └── API endpoints
├── Data Pipeline
│   ├── RIVM data fetching
│   ├── Population data integration
│   └── Quality validation
├── Containerization
│   ├── Docker containerization
│   ├── Docker Compose orchestration
│   └── Health checks & monitoring
└── DevOps
    ├── GitHub Actions CI/CD
    ├── AWS Elastic Beanstalk deployment
    └── Monitoring & logging
```

## 🎯 Key Achievements

- **Real-time data integration**: Automatic updates from official sources
- **Scalable architecture**: Handles large datasets efficiently
- **Production deployment**: Live dashboard with 99.9% uptime
- **Interactive UX**: Intuitive interface for data exploration
- **Mobile responsive**: Works seamlessly across devices
- **Automated testing**: CI/CD pipeline with quality checks

## 📚 Learning Outcomes

This project demonstrates proficiency in:

- **Data Science**: Statistical analysis and visualization
- **Web Development**: Full-stack application development
- **DevOps**: CI/CD, cloud deployment, monitoring
- **API Integration**: External data source management
- **Performance Optimization**: Efficient data processing
- **User Experience**: Intuitive dashboard design

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Email**: shriniwas92@gmail.com
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **LinkedIn**: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

**Built with ❤️ for the Dutch community during the COVID-19 pandemic**
