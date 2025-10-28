# Freshly - ADHD-Friendly Pantry & Fridge Inventory Manager

A full-stack web application designed specifically for ADHD users to manage pantry and fridge inventory, reduce food waste, and simplify meal planning through AI-powered receipt scanning and smart automation.

## Features

### 🧾 AI-Powered Receipt Processing
- Scan paper receipts with your phone camera
- Upload digital receipts (PDF, screenshots)
- Extract line items in under 2 seconds
- Smart product matching to existing inventory
- Bulk add with edit capability
- Duplicate receipt detection
- Multi-receipt batch processing
- Receipt archive with search
- Auto-categorization from merchant data
- Online grocery order email parsing (Instacart, Amazon Fresh)
- Price comparison with purchase history

### 📦 Flexible Inventory Management
- Multiple unit types (weight, volume, count, servings)
- Partial usage tracking with visual sliders
- Barcode scanner backup
- Voice input support
- Manual entry with smart autocomplete
- Multi-location tracking (fridge, freezer, pantry, custom zones)
- Purchase and expiration date tracking
- FIFO visual indicators
- Recipe yield calculator for auto-deduction

### 🧠 ADHD-Optimized UX
- **UNDO/REDO** for ALL actions
- Batch operations
- Visual color-coded dashboard with minimal text
- 2-click-max interface for common actions
- Drag-and-drop functionality
- Persistent floating add button
- Offline-first with auto-save (zero data loss)
- Progress indicators for long operations
- Forgiving error handling with helpful messages

### 🍎 Smart Waste Prevention
- "Eat First" priority queue (expiring soon + leftovers)
- Duplicate purchase detection while shopping
- Customizable expiration warnings (3/5/7 days)
- Daily digest notifications with snooze
- Waste tracking analytics
- Money saved counter
- Environmental impact dashboard (CO2, water saved)

### 🍳 AI Meal Planning
- AI meal suggestions from current inventory (OpenAI/Anthropic)
- Ingredient-based recipe search
- "Use up leftovers" meal type
- Weekly calendar view
- Recipe database with scaling
- Dietary filters (vegan, gluten-free, etc.)
- Recipe import from URLs

### 🛒 Smart Shopping Lists
- Auto-generated from meal plans
- Inventory-check-before-adding
- Price tracking per item
- Store aisle organization
- Household sharing with real-time sync
- Quick-add recent purchases
- Staples list

### 📊 Analytics & Insights
- Spending trends over time
- Most-wasted items report
- Category breakdowns
- Savings goals tracking
- Streak tracking (days without waste)
- Achievement badges
- Export to CSV/PDF

### 👨‍👩‍👧‍👦 Family Features
- Multi-user accounts with permission levels (admin/editor/viewer)
- Real-time sync across devices
- Shared shopping lists
- Expense splitting

## Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL** database
- **SQLAlchemy** ORM with Alembic migrations
- **JWT** authentication with refresh tokens
- **Pydantic** for validation
- **Receipt OCR**: Veryfi/Mindee/Taggun API integration
- **AI**: OpenAI API for meal suggestions

### Frontend
- **React 18+** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** for styling
- **React Query** for server state management
- **Zustand** for client state management
- **React Router v6** for routing
- **Recharts** for analytics visualization
- **react-scanner** for barcode scanning
- **Framer Motion** for animations
- **PWA** with service workers for offline support
- **IndexedDB** for local storage

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- API keys for:
  - Receipt OCR service (Veryfi, Mindee, or Taggun)
  - OpenAI API (for meal suggestions)

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd freshly
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env with your database credentials and API keys
# DATABASE_URL=postgresql://user:password@localhost:5432/freshly
# SECRET_KEY=your-secret-key-here
# RECEIPT_OCR_API_KEY=your-ocr-api-key
# OPENAI_API_KEY=your-openai-api-key

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

Backend will run at: http://localhost:8000

API documentation available at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file from template
cp .env.example .env

# Edit .env with your backend URL
# VITE_API_URL=http://localhost:8000

# Start the development server
npm run dev
```

Frontend will run at: http://localhost:5173

## Deployment

### Backend Deployment (Railway/Render)

1. Set environment variables in your hosting platform
2. Connect your GitHub repository
3. The platform will automatically detect and deploy the FastAPI app
4. Run migrations: `alembic upgrade head`

### Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variable: `VITE_API_URL` pointing to your backend URL

## Project Structure

```
freshly/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── inventory.py
│   │   │   │   ├── receipts.py
│   │   │   │   ├── meals.py
│   │   │   │   ├── shopping.py
│   │   │   │   └── analytics.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── inventory.py
│   │   │   ├── receipt.py
│   │   │   ├── meal.py
│   │   │   └── shopping.py
│   │   ├── schemas/
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ocr_service.py
│   │   │   ├── ai_service.py
│   │   │   └── notification_service.py
│   │   ├── db/
│   │   │   └── session.py
│   │   └── main.py
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.example
└── README.md
```

## Usage

### First Time Setup

1. Create an account at the login page
2. Set up your household (optional - add family members)
3. Configure your storage locations (fridge, freezer, pantry, etc.)

### Adding Items

**Method 1: Scan Receipt (Recommended)**
1. Click the floating camera button
2. Take a photo of your receipt or upload a digital receipt
3. Wait 1-2 seconds for processing
4. Review and edit extracted items
5. Confirm to add all items to inventory

**Method 2: Barcode Scanner**
1. Click the floating add button
2. Select "Scan Barcode"
3. Point camera at product barcode
4. Enter quantity and expiration date

**Method 3: Manual Entry**
1. Click the floating add button
2. Start typing product name (autocomplete will suggest)
3. Select quantity and unit
4. Set expiration date (or let AI estimate)

### Meal Planning

1. Go to "Meal Plan" tab
2. Click "Get AI Suggestions" for meal ideas using your current inventory
3. Or search recipes by ingredients
4. Add meals to your weekly calendar
5. Generate shopping list for missing ingredients

### Shopping

1. Go to "Shopping" tab
2. View auto-generated list from meal plans
3. Or add items manually
4. Check off items as you shop
5. Scan receipt when done to auto-update inventory

### Waste Tracking

1. When you discard food, mark it as "wasted" in inventory
2. View waste analytics in the "Analytics" tab
3. See money saved counter and environmental impact
4. Track your no-waste streak

## API Documentation

Full API documentation is available at `/docs` when running the backend server.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ for ADHD brains that deserve better tools
