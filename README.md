# Family Meal Planner

A web application for managing family meals, including recipe storage, ingredient tracking, meal scheduling, and shopping list generation.

## Tech Stack

- **Backend:** Django 5.x, PostgreSQL 16
- **Frontend:** HTMX, Alpine.js, Tailwind CSS
- **Infrastructure:** Docker, uv, npm

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- uv (Python package manager)
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd MealPlanning
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations:**
   ```bash
   uv run python manage.py migrate
   ```

5. **Start development servers:**
   ```bash
   # Terminal 1: Django
   uv run python manage.py runserver

   # Terminal 2: Tailwind watch
   npm run dev
   ```

6. **Visit:** http://localhost:8000

### Docker Development

```bash
# Start PostgreSQL and Django
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run migrations
docker compose exec web uv run python manage.py migrate
```

## Project Structure

```
├── apps/           # Django applications
│   ├── recipes/    # Recipe management
│   ├── planning/   # Meal planning
│   └── shopping/   # Shopping lists
├── config/         # Django settings
├── templates/      # HTML templates
├── static/         # CSS, JS, images
└── media/          # User uploads
```

## Documentation

- [Technical Specification](Family_Meal_Planner_Spec.md)
- [Claude Code Context](CLAUDE.md)
