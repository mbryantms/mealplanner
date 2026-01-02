# Family Meal Planner

**Technical Specification Document**

*Version 1.0 - MVP Definition*

---

## Project Overview

A web application for managing family meals, including recipe storage, ingredient tracking, meal scheduling, and shopping list generation. Designed for single-household use with shared access for all family members.

---

## Technology Stack

### Backend

- **Framework:** Django 5.x (Python 3.12+)
- **Database:** PostgreSQL
- **ORM:** Django ORM with normalized schema
- **Authentication:** Django built-in auth (single household, shared login or individual accounts TBD)

### Frontend

- **Interactivity:** HTMX for dynamic updates without full page reloads
- **Reactivity:** Alpine.js for lightweight client-side state management
- **Styling:** Tailwind CSS for utility-first styling
- **Templates:** Django templates with HTMX partials

### Infrastructure

- **Containerization:** Docker / Docker Compose
- **Deployment:** TBD (self-hosted or VPS)
- **Package Management:** uv for Python, npm for frontend tooling

---

## Data Model

The database uses a normalized structure to enable ingredient reuse across recipes and intelligent shopping list aggregation.

### Core Entities

#### Ingredient (Master List)

A canonical list of ingredients used across all recipes.

- **id:** Primary key (UUID or auto-increment)
- **name:** Ingredient name (e.g., "Chicken Breast", "Olive Oil")
- **category:** FK to IngredientCategory (Produce, Dairy, Meat, Pantry, etc.)
- **default_unit:** Default measurement unit (oz, lb, cups, etc.)
- **notes:** Optional notes (e.g., "boneless skinless preferred")

#### Recipe

A meal that can be prepared and scheduled.

- **id:** Primary key
- **name:** Recipe title
- **description:** Brief description
- **instructions:** Preparation steps (Markdown or plain text)
- **prep_time:** Time in minutes for preparation
- **cook_time:** Time in minutes for cooking
- **total_time:** Computed or overridable total time
- **servings:** Default serving count (integer)
- **makes_leftovers:** Boolean flag
- **leftover_days:** Optional: how many days leftovers typically last
- **source_url:** Optional: original recipe URL (for future scraping)
- **image:** Optional: recipe photo
- **created_at:** Timestamp
- **updated_at:** Timestamp

#### RecipeIngredient (Junction Table)

Links recipes to ingredients with quantities.

- **recipe:** FK to Recipe
- **ingredient:** FK to Ingredient
- **quantity:** Decimal amount
- **unit:** Unit override (or use ingredient default)
- **preparation:** Optional modifier (e.g., "diced", "minced")
- **optional:** Boolean for optional ingredients

#### Category

Hierarchical grouping for recipes (e.g., Cuisine > Italian > Pasta).

- **id:** Primary key
- **name:** Category name
- **parent:** Self-referential FK for hierarchy (nullable)

#### Tag

Flat labels for flexible filtering (e.g., "Quick", "Kid-Friendly", "Vegetarian").

- **id:** Primary key
- **name:** Tag name
- **slug:** URL-safe identifier

#### MealPlan

A scheduled meal assignment.

- **id:** Primary key
- **date:** Date of the meal
- **meal_type:** Enum: BREAKFAST, LUNCH, DINNER (default: DINNER)
- **recipe:** FK to Recipe (nullable for custom entries)
- **custom_meal:** Text field for non-recipe meals (e.g., "Takeout")
- **servings_override:** Optional serving count adjustment
- **notes:** Optional notes for this specific meal instance

#### ShoppingList

Generated or manual shopping list.

- **id:** Primary key
- **name:** List name (e.g., "Week of Jan 6")
- **created_at:** Timestamp
- **date_range:** Optional start/end dates if generated from meal plan

#### ShoppingListItem

- **shopping_list:** FK to ShoppingList
- **ingredient:** FK to Ingredient (nullable for custom items)
- **custom_item:** Text for non-ingredient items
- **quantity:** Aggregated quantity
- **unit:** Unit of measurement
- **checked:** Boolean for check-off functionality

#### IngredientCategory

Groups ingredients by store section for organized shopping lists.

- **id:** Primary key
- **name:** Category name (Produce, Dairy, Meat, Frozen, Pantry, etc.)
- **sort_order:** Display order for shopping list organization

---

## MVP Features

### Recipe Management

- Create, read, update, delete recipes
- Add ingredients from master list (with autocomplete)
- Create new ingredients on-the-fly during recipe entry
- Assign categories and tags to recipes
- Search and filter recipes by name, category, tag, ingredient
- View recipe with scaled ingredient quantities

### Meal Planning

- Weekly calendar view (Monday-Sunday)
- Assign recipes to specific dates and meal types
- Quick "Leftovers" and "Takeout" options
- Navigate between weeks
- Visual indicator for leftover-friendly meals

### Shopping Lists

- Generate shopping list from date range of meal plan
- Aggregate duplicate ingredients across recipes
- Group items by ingredient category (store aisle)
- Check off items (persisted state)
- Add custom items not in ingredient database
- Mobile-friendly interface for in-store use

### User Interface

- Responsive design (desktop and mobile)
- HTMX-powered interactions (no full page reloads)
- Simple navigation: Recipes, Plan, Shopping List
- PWA capability for add-to-homescreen

---

## Future Features (Post-MVP)

- Recipe import via URL scraping
- Nutritional information (API integration or manual)
- Meal suggestions based on history
- Pantry inventory tracking
- Cost estimation per meal/week
- Recipe sharing/export
- Grocery delivery service integration
- User accounts with individual preferences

---

## Open Questions to Finalize MVP

*The following decisions should be made before development begins:*

### Authentication & Access

1. Single shared household login, or individual family member accounts?
2. If individual accounts: any permission differences (e.g., kids view-only)?
3. Password reset mechanism needed for MVP?

### Recipe Entry

4. Instructions format: plain text, Markdown, or rich text editor?
5. Photo upload required for MVP, or optional/later?
6. Pre-seed common ingredients, or start with empty database?

### Meal Planning

7. Week starts on Sunday or Monday?
8. Show all three meal slots by default, or just dinner with option to add others?
9. Drag-and-drop interaction for MVP, or simple select/assign?

### Shopping List

10. Unit conversion needed (e.g., combine 8oz + 1lb of same ingredient)?
11. Default ingredient categories to pre-populate?
12. Offline support for shopping list (service worker)?

### Deployment

13. Self-host on home lab (Proxmox), or external VPS?
14. Domain name / SSL certificate approach?
15. Backup strategy for database?

### Data & Content

16. Import existing recipes from another source, or fresh start?
17. Any specific categories/tags to pre-create?

---

## Appendix: Entity Relationship Summary

Key relationships in the data model:

| Relationship | Description |
|--------------|-------------|
| Recipe → Ingredient | Many-to-many via RecipeIngredient |
| Recipe → Category | Many-to-one (recipe belongs to one category) |
| Recipe → Tag | Many-to-many |
| MealPlan → Recipe | Many-to-one (nullable for custom meals) |
| ShoppingList → Ingredient | Many-to-many via ShoppingListItem |
| Ingredient → Category | Many-to-one (for shopping list grouping) |
| Category → Category | Self-referential (parent for hierarchy) |
