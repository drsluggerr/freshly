# Getting Started with Freshly

This guide will help you set up and run Freshly locally on your machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **PostgreSQL 14+** ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))

Optional but recommended:
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/)) - For easy local development

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd freshly

# 2. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Edit backend/.env and add your API keys
# - Get Veryfi API key from: https://www.veryfi.com/
# - Get OpenAI API key from: https://platform.openai.com/api-keys

# 4. Start all services
docker-compose up

# The app will be available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

That's it! Skip to the "First Time Setup" section below.

## Manual Setup (Without Docker)

### Step 1: Set Up the Database

```bash
# Start PostgreSQL service (varies by OS)
# On Mac with Homebrew:
brew services start postgresql

# On Windows, start from Services or pgAdmin

# Create the database
createdb freshly

# Or using psql:
psql -U postgres
CREATE DATABASE freshly;
\q
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your settings:
# - Update DATABASE_URL if needed
# - Add SECRET_KEY (generate with: openssl rand -hex 32)
# - Add API keys (Veryfi, OpenAI)

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload

# Backend will run at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Step 3: Frontend Setup

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env file:
# VITE_API_URL=http://localhost:8000

# Start the development server
npm run dev

# Frontend will run at http://localhost:5173
```

## First Time Setup

1. **Open your browser** and go to http://localhost:5173

2. **Create an account:**
   - Click "Don't have an account? Sign up"
   - Fill in your details
   - Click "Create Account"

3. **Set up your household:**
   - After login, you'll be on the dashboard
   - Add storage locations (Fridge, Freezer, Pantry, etc.)

4. **Add your first items:**
   - Option 1: Click the floating + button → "Scan Receipt"
   - Option 2: Manually add items from the Inventory page

5. **Explore features:**
   - 📦 **Inventory**: View and manage all items
   - 🛒 **Shopping**: Create shopping lists
   - 🍳 **Meals**: Get AI meal suggestions
   - 📊 **Analytics**: Track waste and spending

## Getting API Keys

### Veryfi (Receipt OCR)

1. Go to https://www.veryfi.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Copy your:
   - API Key
   - Client ID
   - Username
5. Add to `backend/.env`:
   ```
   VERYFI_API_KEY=your_api_key
   VERYFI_CLIENT_ID=your_client_id
   VERYFI_USERNAME=your_username
   ```

**Free tier:** 200 receipts/month

### Alternative: Mindee (Receipt OCR)

1. Go to https://mindee.com/
2. Sign up for free account
3. Get API key from dashboard
4. Add to `backend/.env`:
   ```
   MINDEE_API_KEY=your_api_key
   ```

### OpenAI (AI Meal Suggestions)

1. Go to https://platform.openai.com/
2. Sign up/login
3. Navigate to API Keys section
4. Create new secret key
5. Add to `backend/.env`:
   ```
   OPENAI_API_KEY=your_api_key
   ```

**Pricing:** ~$0.002 per meal suggestion request

### Alternative: Anthropic Claude (AI Meal Suggestions)

1. Go to https://console.anthropic.com/
2. Sign up for account
3. Get API key
4. Add to `backend/.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key
   ```

## Common Issues

### Backend won't start

**Error: "database freshly does not exist"**
```bash
createdb freshly
alembic upgrade head
```

**Error: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Error: "alembic.util.exc.CommandError"**
```bash
# Make sure you're in the backend directory
cd backend
alembic upgrade head
```

### Frontend won't start

**Error: "command not found: npm"**
- Install Node.js from https://nodejs.org/

**Error: "Cannot find module"**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Error: "Failed to fetch" in browser**
- Make sure backend is running at http://localhost:8000
- Check VITE_API_URL in frontend/.env

### Database connection issues

**Error: "could not connect to server"**
- Make sure PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Verify username/password are correct

**On Windows:**
```bash
# Check if PostgreSQL is running
services.msc
# Look for "postgresql" service and start it
```

**On Mac:**
```bash
# Check status
brew services list

# Start PostgreSQL
brew services start postgresql
```

### Receipt upload not working

- Check if OCR API key is valid
- Verify you're within free tier limits
- Check backend logs for errors
- Try with a clear, well-lit receipt photo

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Backend: Changes to Python files auto-reload
- Frontend: Changes to React files auto-reload

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation where you can:
- View all endpoints
- Test API calls
- See request/response schemas

### Database GUI

Recommended tools for viewing/editing database:
- **pgAdmin** (https://www.pgadmin.org/)
- **DBeaver** (https://dbeaver.io/)
- **TablePlus** (https://tableplus.com/)

Connection details:
- Host: localhost
- Port: 5432
- Database: freshly
- Username: postgres
- Password: postgres (or your configured password)

### Debugging

**Backend:**
```python
# Add breakpoints in VS Code or use pdb
import pdb; pdb.set_trace()
```

**Frontend:**
```typescript
// Use browser DevTools
console.log('Debug:', variable)
debugger; // Pauses execution
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Next Steps

Now that you have Freshly running:

1. **Try the main features:**
   - Upload a receipt
   - Add items to inventory
   - Get AI meal suggestions
   - Create a shopping list

2. **Customize:**
   - Add your storage locations
   - Set up your preferred categories
   - Configure expiration warnings

3. **Learn more:**
   - Read the full README.md
   - Check out DEPLOYMENT.md for production setup
   - Explore the API at /docs

4. **Contribute:**
   - Report bugs on GitHub
   - Suggest features
   - Submit pull requests

## Getting Help

If you run into issues:

1. Check this guide's "Common Issues" section
2. Review the logs:
   - Backend: Terminal running uvicorn
   - Frontend: Browser DevTools console
3. Open an issue on GitHub with:
   - Description of the problem
   - Error messages
   - Steps to reproduce

## Stopping the App

**With Docker:**
```bash
docker-compose down
```

**Manual:**
- Press Ctrl+C in both terminal windows (backend and frontend)
- Optionally stop PostgreSQL service

## Resetting Everything

**With Docker:**
```bash
docker-compose down -v  # Removes all data
docker-compose up
```

**Manual:**
```bash
# Drop and recreate database
dropdb freshly
createdb freshly

# Rerun migrations
cd backend
alembic upgrade head

# Frontend doesn't need reset (no local data)
```

---

**Congratulations!** You now have Freshly running locally. Enjoy managing your pantry! 🎉
