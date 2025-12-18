# Quick Start Guide - Running the Project

## Prerequisites Check ✅
- ✅ Python 3.11.4 installed
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ .env file configured

## Step-by-Step Instructions

### Step 1: Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 2: Verify .env File

Make sure your `.env` file contains at minimum:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Run the Application

**Option A: Using uvicorn directly (Recommended)**
```bash
uvicorn main:app --reload
```

**Option B: Using Python**
```bash
python -m uvicorn main:app --reload
```

**Option C: Run with custom host/port**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Verify It's Running

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 5: Test the API

**Open in browser:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- API Root: http://localhost:8000

**Or use curl:**
```bash
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/
```

## Common Issues & Solutions

### Issue: "GEMINI_API_KEY not found"
**Solution:** Make sure your `.env` file exists in the project root and contains `GEMINI_API_KEY=your_key`

### Issue: "Module not found"
**Solution:** Activate virtual environment and install dependencies:
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution:** Use a different port:
```bash
uvicorn main:app --reload --port 8001
```

### Issue: PowerShell execution policy error
**Solution:** Run this in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

1. **Get a JWT Token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" -u "username:password"
   ```

2. **Analyze a Sector:**
   ```bash
   curl -X GET "http://localhost:8000/analyze/pharmaceuticals" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Or use the example script:**
   ```bash
   python example_usage.py
   ```

## Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

