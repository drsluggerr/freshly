# Freshly - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Option 1: Docker (Easiest)

```bash
# 1. Clone and navigate
git clone <your-repo>
cd freshly

# 2. Set up environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Start everything
docker-compose up

# ✅ Done! Visit http://localhost:5173
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# Create database
createdb freshly

# Configure .env file
cp .env.example .env
# Edit .env and add your API keys

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit http://localhost:5173 and create an account!

## 🔑 API Keys (Optional but Recommended)

### Free Receipt OCR (200/month)
1. Sign up: https://www.veryfi.com/
2. Get API key from dashboard
3. Add to `backend/.env`:
   ```
   VERYFI_API_KEY=your_key
   VERYFI_CLIENT_ID=your_client_id
   VERYFI_USERNAME=your_username
   ```

### AI Meal Suggestions
1. Sign up: https://platform.openai.com/
2. Create API key
3. Add to `backend/.env`:
   ```
   OPENAI_API_KEY=your_key
   ```

## 📱 First Steps After Login

1. **Add Items** - Click floating + button → Upload Receipt
2. **View Inventory** - See all your items in Inventory tab
3. **Get Meal Ideas** - Go to Meals → Click "Get AI Meal Ideas"
4. **Track Analytics** - Check Analytics for insights

## 🛠 Common Commands

```bash
# Backend
alembic upgrade head      # Run migrations
alembic revision -m "msg" # Create migration
pytest                    # Run tests

# Frontend
npm run dev              # Start dev server
npm run build            # Production build
npm run preview          # Preview build

# Docker
docker-compose up        # Start all services
docker-compose down      # Stop all services
docker-compose down -v   # Reset everything
```

## 📚 Full Documentation

- **Setup Guide**: `GETTING_STARTED.md`
- **Deployment**: `DEPLOYMENT.md`
- **Contributing**: `CONTRIBUTING.md`
- **Project Details**: `PROJECT_SUMMARY.md`

## 🆘 Having Issues?

1. Check `GETTING_STARTED.md` → Common Issues section
2. Ensure PostgreSQL is running
3. Verify .env files are configured
4. Check logs in terminal
5. Open an issue on GitHub

## ✨ Key Features

- 📸 **Receipt Scanning** - Auto-extract items from receipts
- 🤖 **AI Meal Suggestions** - Get recipes from your inventory
- 📊 **Waste Tracking** - See what you're wasting and save money
- 🛒 **Smart Shopping** - Auto-generated shopping lists
- ⏮️ **Undo/Redo** - Forgiving interface for ADHD brains
- 📱 **Mobile Friendly** - PWA support for offline use

## 🎯 Quick Tips

- Use the **floating + button** for quick actions
- Check **"Eat First"** on dashboard daily
- Enable **notifications** for expiration reminders
- Use **barcode scanner** for quick item adding (coming soon)
- **Undo** is always available (Ctrl+Z or navbar button)

---

Happy organizing! 🎉
