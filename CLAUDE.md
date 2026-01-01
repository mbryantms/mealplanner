# Family Meal Planner - Claude Code Context

This document provides context for Claude Code when working on this project.

## Project Overview

A web application for managing family meals, including recipe storage, ingredient tracking, meal scheduling, and shopping list generation. Designed for single-household use with shared access for all family members.

See `Family_Meal_Planner_Spec.md` for the full specification.

## Technology Stack

### Backend
- **Python 3.12+** with **Django 5.x**
- **PostgreSQL 16** for production database (SQLite for local dev)
- **django-environ** for environment configuration
- **uv** for Python package management

### Frontend
- **HTMX** for dynamic interactions without full page reloads
- **Alpine.js** for lightweight client-side reactivity
- **Tailwind CSS** for utility-first styling
- **Django templates** with HTMX partials

### Infrastructure
- **Docker** / **Docker Compose** for containerization
- **WhiteNoise** for static file serving
- **Gunicorn** as the WSGI server

## Project Structure

```
MealPlanning/
├── apps/                    # Django applications
│   ├── recipes/             # Recipe and ingredient management
│   ├── planning/            # Meal planning and calendar
│   └── shopping/            # Shopping list generation
├── config/                  # Django project configuration
│   ├── settings.py          # Main settings (uses django-environ)
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── templates/               # Global templates
│   └── base.html            # Base template with nav, HTMX, Alpine
├── static/                  # Static assets
│   ├── css/
│   │   ├── input.css        # Tailwind source
│   │   └── output.css       # Compiled CSS (gitignored)
│   └── js/
│       └── vendor/          # HTMX, Alpine.js
├── media/                   # User uploads (gitignored)
├── pyproject.toml           # Python dependencies (uv)
├── package.json             # Node dependencies (Tailwind)
├── tailwind.config.js       # Tailwind configuration
├── Dockerfile               # Production container
├── Dockerfile.dev           # Development container
├── docker-compose.yml       # Production compose
├── docker-compose.dev.yml   # Development compose overlay
└── manage.py                # Django management script
```

## Development Commands

### Python/Django (using uv)

```bash
# Sync dependencies
uv sync

# Run development server
uv run python manage.py runserver

# Run migrations
uv run python manage.py migrate

# Create new migrations
uv run python manage.py makemigrations

# Create superuser
uv run python manage.py createsuperuser

# Run tests
uv run pytest

# Linting
uv run ruff check .
uv run ruff format .
```

### Frontend (using npm)

```bash
# Install dependencies
npm install

# Watch mode (development)
npm run dev

# Build for production
npm run build
```

### Docker

```bash
# Start production stack
docker compose up -d

# Start development stack with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# View logs
docker compose logs -f web

# Run Django command in container
docker compose exec web uv run python manage.py migrate
```

## Code Conventions

### Python
- Use **ruff** for linting and formatting
- Line length: 88 characters
- Follow Django conventions for models, views, URLs
- Use type hints where practical
- Tests go in `tests/` directory within each app

### Templates
- Use Django template language with HTMX attributes
- HTMX partials should be in `templates/<app>/partials/`
- Use Alpine.js `x-data` for local component state
- Keep JavaScript minimal; prefer HTMX + Alpine

### CSS
- Use Tailwind utility classes exclusively
- Custom styles only when Tailwind is insufficient
- Put custom styles in `static/css/input.css`

### Git
- Conventional commit messages (feat:, fix:, docs:, etc.)
- Keep commits focused and atomic

## Environment Variables

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | Django secret key | Required |
| `DATABASE_URL` | Database connection string | SQLite |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `[]` |

## Data Model Summary

See `Family_Meal_Planner_Spec.md` for full details. Key entities:

- **Ingredient**: Master list of ingredients with categories
- **Recipe**: Meals with instructions, times, servings
- **RecipeIngredient**: Junction linking recipes to ingredients with quantities
- **MealPlan**: Scheduled meal assignments by date
- **ShoppingList/ShoppingListItem**: Generated shopping lists

## Open Questions

The spec contains open questions (section "Open Questions to Finalize MVP") that should be resolved before implementing features. Consult the user about these when relevant.
