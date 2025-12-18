
# Water Quality Logging System

Django web application for logging and viewing water quality measurements for various water bodies. 
---

## Features

- Log water quality measurements
- View all water bodies and measurements on a dashboard
- Interactive map of water body locations
- Admin interface

---

## Core Models

- **WaterBody**: Name, type, latitude, longitude, description
- **WaterQualityMeasurement**: Water body, date, pH, dissolved oxygen, temperature, notes

---

## Tech Stack

- Django
- SQLite (default database)
- Leaflet (map)

---

## Setup & Installation

1. Build Docker image:
   
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Load data:
   ```bash
   python manage.py create_data
   ```
4. Start the server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

---

Visit:
- Dashboard: http://localhost:8000
- Admin: http://localhost:8000/admin

---

## Usage Guide

- Go to http://localhost:8000 to view the dashboard and map
- Click "Submit Data" to add a new measurement
- Use the admin panel at http://localhost:8000/admin to manage data

---

## Testing

To run tests:
```bash
pytest --ds=aquawatch.settings
```

---