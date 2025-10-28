# Contributing to Freshly

Thank you for considering contributing to Freshly! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and considerate of others. We're building a tool to help people with ADHD manage their lives better - let's keep the community supportive and welcoming.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details:**
  - OS (Windows, Mac, Linux)
  - Browser (if frontend issue)
  - Python/Node version
  - Error messages from logs

### Suggesting Features

Feature requests are welcome! Please:

1. Check if the feature has already been suggested
2. Explain the use case and why it would be valuable
3. Consider how it fits with ADHD-friendly design principles:
   - Visual over text-heavy
   - Minimal clicks/steps
   - Forgiving (undo/redo)
   - Progress indicators
   - Clear feedback

### Pull Requests

1. **Fork the repository** and create your branch from `main`

2. **Set up your development environment:**
   ```bash
   # See GETTING_STARTED.md for full setup
   docker-compose up
   ```

3. **Make your changes:**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes:**
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm test
   ```

5. **Commit your changes:**
   ```bash
   git commit -m "Brief description of changes"
   ```

   Use conventional commit format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `style:` for formatting changes
   - `refactor:` for code refactoring
   - `test:` for adding tests
   - `chore:` for maintenance

6. **Push to your fork and submit a pull request**

## Development Guidelines

### Backend (Python/FastAPI)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions/classes
- Keep functions small and focused
- Use async/await for I/O operations

```python
async def get_inventory_items(
    db: Session,
    household_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[InventoryItem]:
    """
    Retrieve inventory items for a household.

    Args:
        db: Database session
        household_id: ID of the household
        skip: Number of items to skip
        limit: Maximum number of items to return

    Returns:
        List of inventory items
    """
    return db.query(InventoryItem).filter(
        InventoryItem.household_id == household_id
    ).offset(skip).limit(limit).all()
```

### Frontend (React/TypeScript)

- Use functional components with hooks
- Type everything (no `any` types)
- Keep components small (< 200 lines)
- Extract reusable logic to custom hooks
- Use meaningful variable/function names

```typescript
interface InventoryItemProps {
  item: InventoryItem
  onDelete: (id: number) => void
  onUpdate: (id: number, data: Partial<InventoryItem>) => void
}

export const InventoryItemCard: React.FC<InventoryItemProps> = ({
  item,
  onDelete,
  onUpdate
}) => {
  // Component implementation
}
```

### Database Migrations

When changing database schema:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description of changes"

# Review generated migration in alembic/versions/
# Make any necessary adjustments

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

### ADHD-Friendly Design Principles

When adding new features, consider:

1. **Reduce cognitive load:**
   - Use icons and colors for quick scanning
   - Minimize text when possible
   - Group related actions together

2. **Minimize steps:**
   - Can this be done in 2 clicks instead of 5?
   - Use sensible defaults
   - Auto-save when possible

3. **Provide clear feedback:**
   - Show loading states
   - Confirm actions with toasts
   - Display progress for multi-step processes

4. **Be forgiving:**
   - Implement undo/redo
   - Confirm destructive actions
   - Allow editing after submission

5. **Visual hierarchy:**
   - Most important actions should be prominent
   - Use color to indicate urgency/status
   - Consistent spacing and alignment

## Project Structure

```
freshly/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   └── alembic/          # Database migrations
│
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── ui/       # Reusable UI components
│   │   │   └── layout/   # Layout components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API clients
│   │   ├── store/        # State management
│   │   ├── types/        # TypeScript types
│   │   └── utils/        # Helper functions
│   └── public/           # Static assets
│
├── docs/                 # Additional documentation
└── tests/                # Test files
```

## Testing

### Backend Tests

```python
# tests/test_inventory.py
import pytest
from fastapi.testclient import TestClient

def test_create_inventory_item(client: TestClient, auth_headers):
    response = client.post(
        "/api/v1/inventory",
        json={
            "name": "Test Item",
            "category": "produce",
            "quantity": 1,
            "unit": "item"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

### Frontend Tests

```typescript
// components/InventoryItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { InventoryItemCard } from './InventoryItemCard'

describe('InventoryItemCard', () => {
  it('renders item details', () => {
    const item = {
      id: 1,
      name: 'Test Item',
      quantity: 5,
      unit: 'item'
    }

    render(<InventoryItemCard item={item} />)

    expect(screen.getByText('Test Item')).toBeInTheDocument()
    expect(screen.getByText('5 item')).toBeInTheDocument()
  })
})
```

## Documentation

When adding features:

1. Update relevant README sections
2. Add JSDoc/docstrings to code
3. Update API documentation (backend/app/main.py)
4. Add examples to GETTING_STARTED.md if needed

## Questions?

- Open an issue for questions
- Tag with `question` label
- Be specific about what you need help with

## Recognition

Contributors will be added to README.md and release notes.

Thank you for helping make Freshly better! 🎉
