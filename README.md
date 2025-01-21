# What Weather
---

Flask-based weather application that provides real-time weather data through the WeatherStack API, featuring Redis caching, PostgreSQL storage, and a containerized deployment architecture.

## Architecture

- **Web Framework**: Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Web Server**: Nginx (Reverse Proxy)
- **Containerization**: Docker & Docker Compose
- **Authentication**: Custom user authentication system

## Features

- User authentication (register/login)
- Weather data retrieval by city name
- Redis-based caching system (TTL: 1 hour)
- Search history tracking per user
- Healthcheck endpoint
- SSL/TLS support
- IP access restriction for security



## Installation

1. Clone the repository:

```bash
git clone https://github.com/alberefe/what_weather
cd what_weather
```

2.Dependencies

I use uv for dependencies so:

```
$ uv sync
```

Will use the uv.lock file to manage all the necessary dependencies.

3. Create a .env file in the root directory with the following data:

```
WEATHERSTACK_API_KEY=your_weatherstack_api_key
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_flask_app_secret_key
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=postgres
DB_PORT=5432
DB_NAME=flask_app_database
```

Make sure you replace the corresponding dummy data for the relevant.

4. Create your self signed certificates (or place yours) in /certs    (relative to the root directory of the project)

5. Modify the template for nginx and write your own data, like your server ip.


6. Run the application using docker compose

```
$ docker-compose up --build
```

or

```
$ docker-compose up -d
```

## API Endpoints

- `/weather/`: Main endpoint for weather queries
- `/weather/history`: View search history (authenticated users only)
- `/auth/register`: User registration
- `/auth/login`: User login
- `/auth/logout`: User logout
- `/health`: Application health check

## Architecture Details

### Caching Strategy

- Weather data is cached in Redis with a 1-hour TTL
- Cache keys are formatted as `weather:city:{city_name}`
- Fallback to direct API calls if Redis is unavailable

### Security Features

- Password hashing using Werkzeug's security functions
- SSL/TLS encryption
- IP restriction through Nginx
- Session-based authentication

### Database Schema

- Users table: Stores user credentials and information
- SearchHistory table: Tracks user search history with timestamps

## Docker Configuration

The application runs in four containers:

- `nginx`: Reverse proxy and SSL termination
- `what_weather`: Flask application
- `redis`: Caching server
- `postgres`: Database server


