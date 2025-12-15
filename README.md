# AquaWatch: Water Quality Monitoring System

## Project Overview
AquaWatch is a comprehensive Django web application designed for monitoring and analyzing water quality data across multiple water bodies.

## Models & Features

### Core Models
- **WaterBody Model**: Represents monitored locations (lakes, rivers, reservoirs) with geographic coordinates, type classification, and regulatory information
- **WaterQualityMeasurement Model**: Stores individual water quality readings including pH, dissolved oxygen, temperature, turbidity, nitrates, phosphates, and bacterial counts, linked to specific water bodies and timestamps

### Key Features
- **Data Submission Form**: Interactive web form for field researchers to submit new water quality measurements with validation and GPS coordinate capture
- **Interactive Dashboard**:
  - Real-time ChartJS visualizations showing water quality trends over time
  - Leaflet maps displaying monitoring locations with color-coded quality indicators
  - Alert system for measurements exceeding EPA standards
- **Admin Interface**: Customized Django admin for managing water bodies, reviewing submitted data, and user permissions
- **Data Export Utility**: Generate comprehensive XLSX reports filtered by date range, water body, or parameter thresholds for regulatory compliance
- **Testing Framework**: Comprehensive pytest-django test suite covering models, views, forms, and data export functionality

## Technical Implementation
- **Containerized Deployment**: Docker container with PostgreSQL backend for production scalability
- **CI/CD Pipeline**: GitHub Actions automatically build and test the container on each commit
- **Geographic Integration**: PostGIS extension for spatial queries and mapping capabilities
- **Data Validation**: Form validation ensuring measurement ranges align with scientific standards
- **Responsive Design**: Mobile-friendly interface for field data collection
