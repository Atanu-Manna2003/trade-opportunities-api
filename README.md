# Trade Opportunities API

A production-ready FastAPI service for analyzing Indian market data and generating trade opportunity insights as structured Markdown reports.

## Features

-  **FastAPI** - Modern, fast web framework with async support
-  **JWT Authentication** - Secure token-based authentication
-  **Rate Limiting** - Per-user rate limiting (10 requests/minute by default)
-  **AI-Powered Analysis** - Uses Google Gemini API for intelligent market analysis
-  **Market Data Integration** - Fetches recent market news and data
-  **Structured Reports** - Returns well-formatted Markdown reports
-  **Auto-Generated Docs** - Swagger/OpenAPI documentation at `/docs`

## Project Structure

```
.
├── api/                    # API routes
│   ├── __init__.py
│   ├── routes.py          # Main analysis endpoint
│   └── auth_routes.py     # Authentication endpoints
├── services/              # Business logic services
│   ├── __init__.py
│   ├── search_service.py  # Web search service
│   └── ai_service.py      # Gemini AI service
├── security/              # Security modules
│   ├── __init__.py
│   ├── auth.py            # JWT authentication
│   └── rate_limiter.py    # Rate limiting
├── models/                # Pydantic models
│   ├── __init__.py
│   └── schemas.py         # Request/response schemas
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── logger.py          # Logging configuration
│   └── validators.py      # Input validation
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables example
├── example_usage.py      # Example script demonstrating API usage
└── README.md             # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd assignment
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## Usage

### 1. Get a JWT Token

First, authenticate to get a JWT token:

**Using curl:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -u "username:password" \
  -H "accept: application/json"
```

**Using Python requests:**
```python
import requests

response = requests.post(
    "http://localhost:8000/auth/login",
    auth=("username", "password")
)
token = response.json()["access_token"]
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Analyze a Sector

Use the JWT token to access the analysis endpoint:

**Using curl:**
```bash
curl -X GET "http://localhost:8000/analyze/pharmaceuticals" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "accept: application/json"
```

**Using Python requests:**
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/analyze/pharmaceuticals",
    headers=headers
)

result = response.json()
print(result["report"])  # Markdown report
```

**Response:**
```json
{
  "sector": "pharmaceuticals",
  "report": "# Pharmaceuticals Sector - Trade Opportunities Analysis\n\n## Sector Overview\n...",
  "generated_at": "2024-01-15T10:30:00.123456"
}
```

### 3. Check Rate Limit Status

```bash
curl -X GET "http://localhost:8000/rate-limit-info" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## API Endpoints

### Authentication

- `POST /auth/login` - Get JWT token (HTTP Basic Auth)
- `POST /auth/token` - Alternative token endpoint

### Analysis

- `GET /analyze/{sector}` - Analyze trade opportunities for a sector
  - Requires: JWT token in Authorization header
  - Parameters: `sector` (path parameter)
  - Returns: Markdown report

### Utility

- `GET /` - API information
- `GET /health` - Health check endpoint
- `GET /rate-limit-info` - Get rate limit status
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Report Structure

The generated Markdown report includes:

1. **Sector Overview** - Brief overview of the sector in India
2. **Current Market Trends in India** - Analysis of current trends
3. **Recent News & Signals** - Summary of recent market signals
4. **Trade Opportunities** - Specific trade opportunities and insights
5. **Risks & Challenges** - Potential risks and challenges
6. **Short-term Outlook** - 3-6 months outlook
7. **Disclaimer** - Standard investment disclaimer

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Rate Limiting

Default rate limits:
- **10 requests per minute** per user
- Configurable via environment variables

### JWT Token Expiration

Default token expiration:
- **30 minutes**
- Configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`

## Security Features

- ✅ JWT-based authentication
- ✅ Input validation (sector format validation)
- ✅ Rate limiting per user/session
- ✅ Secure environment variable usage
- ✅ Proper error handling
- ✅ CORS middleware (configurable)

## Example Sectors

You can analyze various Indian market sectors:

- `pharmaceuticals`
- `technology`
- `banking`
- `telecommunications`
- `automotive`
- `real estate`
- `energy`
- `oil and gas`
- `steel`
- `cement`
- `retail`
- `agriculture`
- `healthcare`
- And more...

## Error Handling

The API handles various error scenarios:

- **400 Bad Request** - Invalid sector format
- **401 Unauthorized** - Missing or invalid JWT token
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server errors

All errors return structured JSON responses with error details.

## Example Usage Script

A Python example script is provided to demonstrate API usage:

```bash
# Make sure the API is running first
uvicorn main:app --reload

# In another terminal, run the example
python example_usage.py
```

This script will:
1. Authenticate and get a JWT token
2. Analyze the "pharmaceuticals" sector
3. Save the report to a file
4. Display rate limit information

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

(Add test examples here when tests are implemented)

### Logging

Logs are configured to output to stdout with the following format:
```
YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
```

## Production Deployment

For production deployment:

1. Set proper CORS origins in `main.py`
2. Use environment variables for all secrets
3. Configure proper logging (file-based or centralized)
4. Set up proper monitoring and alerting
5. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
6. Consider adding database persistence for sessions and rate limits
7. Implement proper user management system

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Limitations

- **In-memory storage**: Rate limits and sessions are stored in memory (not persisted)
- **Mock search**: Web search currently uses simplified/mock data (can be enhanced with proper APIs)
- **Simple authentication**: Demo authentication accepts any credentials (should use database in production)

## Future Enhancements

- [ ] Database persistence for sessions and rate limits
- [ ] Proper user management system
- [ ] Integration with real market data APIs
- [ ] Caching layer for reports
- [ ] Background job processing for long-running analyses
- [ ] WebSocket support for real-time updates
- [ ] Export reports as PDF/HTML
- [ ] Historical analysis tracking

## License

This project is provided as-is for evaluation purposes.

## Support

For issues or questions, please refer to the API documentation at `/docs` or contact the development team.

