# Spotter Backend Assessment

Backend API developed for the Spotter Backend Django Engineer assessment.

The API receives a starting location and a destination in the USA, calculates a driving route, finds fuel stations along the route, and determines cost-effective fuel stops based on fuel prices and the vehicle's range.

## Tech Stack

- Python 3.14
- Django 6.1
- Django REST Framework
- OpenRouteService
- SQLite
- Shapely
- Requests

## Features

- Driving route calculation using OpenRouteService.
- Fuel station selection based on proximity to the route.
- Fuel stop selection based on fuel prices and vehicle range.
- Maximum vehicle range of 500 miles.
- Fuel efficiency of 10 MPG.
- Total fuel cost calculation.
- API error handling.
- Automated tests.

## Requirements

- Python 3.14+
- OpenRouteService API key

## Installation

### 1. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the project root:

```env
OPENROUTESERVICE_API_KEY=your_api_key
```

### 4. Database

The project includes the prepared SQLite database with the fuel station data required by the application.

No additional data import is required to run the API.

### 5. Run the server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## API

### Calculate route and fuel stops

**POST** `/api/routes/`

### Request

```json
{
  "start": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "finish": {
    "latitude": 41.8781,
    "longitude": -87.6298
  }
}
```

### Response

The API returns:

- Route distance in miles.
- Route geometry.
- Recommended fuel stops.
- Fuel price at each stop.
- Amount of fuel purchased.
- Cost per stop.
- Total fuel cost.

Example:

```json
{
  "route": {
    "distance_miles": 712.09,
    "geometry": []
  },
  "fuel": {
    "total_cost": 64.88,
    "stops": [
      {
        "station": "SHEETZ #639",
        "location": {
          "latitude": 41.1435785,
          "longitude": -80.721952
        },
        "city": "Youngstown",
        "state": "OH",
        "price_per_gallon": 3.059,
        "distance_from_start_miles": 353.99,
        "gallons": 21.21,
        "cost": 64.88
      }
    ]
  }
}
```

## Fuel Optimization Assumptions

- Vehicle fuel efficiency: **10 MPG**.
- Maximum range: **500 miles**.
- Fuel tank capacity: **50 gallons**.
- The vehicle starts the trip with a full tank.
- The initial tank fill is not included in the calculated cost.
- Fuel stations are considered candidates when they are within approximately 5 miles of the calculated route.
- Fuel prices come from the provided fuel-price dataset.
- When possible, the optimizer prefers cheaper reachable fuel stations.

## Performance

The API uses a single OpenRouteService routing request per API call.

Fuel station candidates are first filtered using a geographic bounding box before calculating their precise distance to the route. This reduces the amount of geometry processing required.

During development:

- New York → Chicago: approximately **1.2 seconds**.
- New York → Los Angeles: approximately **2.2 seconds**.

## Tests

Run the complete test suite with:

```bash
python manage.py test
```

The test suite covers:

- Routes that do not require fuel stops.
- Routes requiring one or multiple fuel stops.
- Selection of cheaper stations.
- Unreachable fuel stations.
- Valid API requests.
- Invalid input.
- Routing errors.
- Unreachable routes.

The current test suite contains **10 tests**.

## Project Structure

```text
assessment_django_spotter/
├── config/
│   ├── settings.py
│   └── urls.py
├── routes/
│   ├── management/
│   ├── migrations/
│   ├── services/
│   │   ├── fuel_optimizer.py
│   │   ├── geocoding.py
│   │   ├── route_geometry.py
│   │   ├── route_planning.py
│   │   └── routing.py
│   ├── tests/
│   │   ├── test_fuel_optimizer.py
│   │   └── test_views.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── data/
│   └── fuel-prices-for-be-assessment.csv
├── db.sqlite3
├── manage.py
├── requirements.txt
└── .env
```

## Notes

Fuel station geocoding is performed as a data preparation step rather than during API requests. This avoids adding external geocoding calls and latency to the route planning endpoint.

The API makes one routing API call per request.

## Interactive route map demo

A small browser interface is available at `/demo/` when the Django development server is running. It calls the existing `POST /api/routes/` endpoint and renders the returned route geometry and fuel stops with Leaflet and OpenStreetMap.

1. Install the dependencies listed in `requirements.txt` in your virtual environment.
2. Set `OPENROUTESERVICE_API_KEY` in your `.env` file.
3. Run migrations if needed with `python manage.py migrate`.
4. Start Django with `python manage.py runserver`.
5. Open `http://127.0.0.1:8000/demo/`.

The demo uses the default coordinates for New York City and Chicago. It requires a working OpenRouteService API key and station records with coordinates along the route. The map uses Leaflet from a CDN and OpenStreetMap tiles, so the browser needs internet access. This UI does not change the existing route-planning algorithm or API response format.
