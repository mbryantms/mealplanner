# Family Meal Planner - MVP Checklist

## Phase 0: Pre-Development Decisions

### Authentication & Access
- [x] ~~Decide: Single shared household login or individual family member accounts?~~ **Individual family member accounts**
- [x] ~~Decide: If individual accounts, any permission differences?~~ **Admin role + general user role**
- [x] ~~Decide: Password reset mechanism needed for MVP?~~ **Yes**

### Recipe Entry
- [ ] Decide: Instructions format (plain text, Markdown, or rich text editor)?
- [ ] Decide: Photo upload required for MVP or optional/later?
- [x] ~~Decide: Pre-seed common ingredients or start empty?~~ **Start empty (fresh start)**

### Meal Planning
- [x] ~~Decide: Week starts on Sunday or Monday?~~ **Sunday**
- [x] ~~Decide: Show all three meal slots by default or just dinner?~~ **Show all meal slots**
- [x] ~~Decide: Drag-and-drop for MVP or simple select/assign?~~ **Drag-and-drop**

### Shopping List
- [x] ~~Decide: Unit conversion needed (e.g., combine 8oz + 1lb)?~~ **No, saved for post-MVP**
- [x] ~~Decide: Default ingredient categories to pre-populate?~~ **No**
- [x] ~~Decide: Offline support via service worker for MVP?~~ **No**

### Deployment
- [x] ~~Decide: Self-host (Proxmox) or external VPS?~~ **Self-host on Proxmox**
- [x] ~~Decide: Domain name and SSL certificate approach?~~ **IP only for now, domain/SSL later**
- [x] ~~Decide: Backup strategy for database?~~ **Deferred to later**

### Data & Content
- [x] ~~Decide: Import existing recipes or fresh start?~~ **Fresh start (maybe example templates)**
- [x] ~~Decide: Specific categories/tags to pre-create?~~ **No**

---

## Phase 1: Data Models

### Ingredient System
- [x] Create `IngredientCategory` model (name, sort_order)
- [x] Create `Ingredient` model (name, category FK, default_unit, notes)
- [x] Create admin interface for IngredientCategory
- [x] Create admin interface for Ingredient
- [x] Add database migration

### Recipe System
- [x] Create `Category` model (name, parent self-FK for hierarchy)
- [x] Create `Tag` model (name, slug)
- [x] Create `Recipe` model (all fields from spec)
- [x] Create `RecipeIngredient` junction model
- [x] Create Recipe-Tag many-to-many relationship
- [x] Create admin interfaces for all recipe models
- [x] Add database migrations

### Meal Planning System
- [x] Create `MealType` enum (BREAKFAST, LUNCH, DINNER)
- [x] Create `MealPlan` model (date, meal_type, recipe FK, custom_meal, servings_override, notes)
- [x] Create admin interface for MealPlan
- [x] Add database migration

### Shopping List System
- [x] Create `ShoppingList` model (name, created_at, date_range)
- [x] Create `ShoppingListItem` model (shopping_list FK, ingredient FK, custom_item, quantity, unit, checked)
- [x] Create admin interfaces for shopping list models
- [x] Add database migration

---

## Phase 2: Recipe Management

### Recipe CRUD
- [x] Create recipe list view (with pagination)
- [x] Create recipe detail view
- [x] Create recipe create form
- [x] Create recipe edit form
- [x] Create recipe delete functionality
- [x] Add URL routing for all recipe views

### Recipe Ingredients
- [x] Create ingredient autocomplete endpoint (HTMX)
- [x] Create inline ingredient add form
- [x] Create on-the-fly ingredient creation modal/form
- [x] Implement ingredient quantity/unit input
- [x] Implement optional ingredient toggle
- [x] Implement preparation notes field

### Recipe Organization
- [x] Create category assignment UI
- [x] Create tag assignment UI (multi-select)
- [ ] Create new category inline creation
- [ ] Create new tag inline creation

### Recipe Search & Filter
- [x] Implement search by recipe name
- [x] Implement filter by category
- [x] Implement filter by tag
- [ ] Implement filter by ingredient
- [x] Create combined search/filter UI
- [x] Add HTMX live search functionality

### Recipe Scaling
- [x] Implement serving size adjustment UI
- [x] Calculate scaled ingredient quantities
- [x] Display scaled quantities in recipe view

### Recipe Image (decision pending)
- [x] Implement image upload field
- [x] Configure media file storage
- [x] Display recipe images in list/detail views
- [x] Add image placeholder for recipes without images

---

## Phase 3: Meal Planning

### Weekly Calendar View
- [x] Create week view template (Sunday-Saturday, 7-day grid)
- [x] Display current week by default
- [x] Show all 3 meal slots per day (Breakfast, Lunch, Dinner)
- [x] Display assigned recipes in slots
- [x] Display custom meals in slots

### Week Navigation
- [x] Add previous/next week buttons
- [x] Add "today" button to return to current week
- [x] Implement week navigation via HTMX
- [x] Display week date range in header

### Meal Assignment
- [x] Create recipe picker/search for assignment
- [x] Implement assign recipe to date/meal_type
- [x] Create quick "Leftovers" option
- [x] Create quick "Takeout" option
- [x] Implement custom meal text entry
- [x] Add servings override option
- [x] Add notes field for meal instance

### Drag-and-Drop
- [x] Implement drag-and-drop library integration
- [x] Make meals draggable between slots
- [x] Make meals draggable between days
- [x] Handle drop validation and persistence
- [ ] Implement copy on drag with modifier key (optional)

### Meal Management
- [x] Implement remove meal from slot
- [ ] Implement copy meal to another day

### Visual Indicators
- [x] Show leftover-friendly meal indicator
- [x] Show recipe image thumbnails (if available)
- [x] Differentiate recipe vs custom meal styling

---

## Phase 4: Shopping Lists

### List Generation
- [x] Create date range picker UI
- [x] Implement "Generate from meal plan" function
- [x] Aggregate ingredients across selected meals
- [x] Handle duplicate ingredient combination (same units only for MVP)
- [x] Group items by ingredient category
- [x] Sort categories by sort_order

### List Display
- [x] Create shopping list view
- [x] Display items grouped by category
- [x] Show quantity and unit for each item
- [x] Display category headers/sections

### Item Check-off
- [x] Implement checkbox for each item
- [x] Persist checked state via HTMX
- [x] Visual styling for checked items
- [ ] Option to hide/show checked items

### Custom Items
- [x] Create "Add custom item" form
- [ ] Allow assigning custom items to categories
- [x] Display custom items in appropriate sections

### List Management
- [x] Create shopping list index (list of lists)
- [x] Implement list rename
- [x] Implement list delete
- [ ] Implement list duplicate/copy

### Mobile Optimization
- [x] Optimize touch targets for check-off
- [x] Ensure readable font sizes on mobile
- [ ] Test category collapse/expand on mobile
- [ ] Minimize data usage for in-store use

---

## Phase 5: User Interface

### Base Layout
- [x] Create responsive base template
- [x] Implement main navigation (Recipes, Plan, Shopping List)
- [x] Add mobile hamburger menu
- [x] Create consistent header/footer

### HTMX Integration
- [x] Configure HTMX for all dynamic interactions
- [x] Create partial templates for HTMX responses
- [x] Implement loading indicators
- [x] Handle HTMX errors gracefully

### Alpine.js Components
- [x] Implement dropdown menus
- [x] Implement modal dialogs
- [x] Implement form validation feedback
- [x] Implement toast notifications

### Tailwind Styling
- [x] Define color palette/theme
- [x] Create consistent button styles
- [x] Create consistent form input styles
- [x] Create consistent card/container styles

### Responsive Design
- [x] Test and fix mobile layouts
- [x] Test and fix tablet layouts
- [x] Ensure touch-friendly interactions
- [ ] Test on actual mobile devices

---

## Phase 6: Authentication

### User System
- [x] Configure Django auth settings
- [x] Create custom User model (or extend) with role field
- [x] Define Admin and User roles/permissions
- [x] Create login page
- [x] Create logout functionality
- [x] Protect all views with login_required

### User Management
- [x] Create user registration (admin-only creation for MVP)
- [x] Create user profile page
- [x] Implement password change
- [x] Implement password reset (email-based)

### Permissions
- [x] Implement admin-only views (user management, etc.)
- [x] Ensure general users can CRUD recipes, meals, lists
- [x] Test permission boundaries

---

## Phase 7: Testing

### Unit Tests
- [ ] Test Ingredient models
- [ ] Test Recipe models
- [ ] Test MealPlan models
- [ ] Test ShoppingList models
- [ ] Test ingredient aggregation logic
- [ ] Test recipe scaling logic

### Integration Tests
- [ ] Test recipe CRUD workflow
- [ ] Test meal planning workflow
- [ ] Test shopping list generation
- [ ] Test search and filter functionality
- [ ] Test authentication flows

### UI/UX Testing
- [ ] Test all HTMX interactions
- [ ] Test drag-and-drop functionality
- [ ] Test form validation
- [ ] Test error handling
- [ ] Cross-browser testing
- [ ] Mobile device testing

---

## Phase 8: Deployment

### Production Configuration
- [ ] Configure production settings
- [ ] Set up environment variables
- [ ] Configure static file serving (WhiteNoise)
- [ ] Configure media file storage
- [ ] Set up logging

### Docker Production
- [ ] Finalize production Dockerfile
- [ ] Create production docker-compose
- [ ] Test production build locally

### Server Setup (Proxmox)
- [ ] Create VM/container on Proxmox
- [ ] Install Docker
- [ ] Configure firewall rules
- [ ] Set up reverse proxy (for future domain)

### Deployment
- [ ] Deploy application
- [ ] Run database migrations
- [ ] Create admin superuser account
- [ ] Verify all functionality via IP

---

## Phase 9: Documentation

- [ ] Update README with deployment instructions
- [ ] Document environment variables
- [ ] Create user guide/help content
- [ ] Update CLAUDE.md with any new patterns

---

## Post-MVP (Deferred Items)

Items explicitly deferred from MVP:
- [ ] Unit conversion for shopping lists (combine 8oz + 1lb)
- [ ] Offline support via service worker / PWA
- [ ] Domain name and SSL certificate
- [ ] Database backup strategy
- [ ] Pre-seeded ingredient categories
- [ ] Dark mode support

---

## Completion Criteria

MVP is complete when:
- [x] All Phase 0 decisions are made
- [x] All data models are implemented and migrated
- [x] Recipe CRUD with ingredients works fully
- [x] Weekly meal planning calendar with drag-and-drop works
- [x] Shopping list generation and check-off works
- [x] Mobile-responsive UI is functional
- [x] Authentication with admin/user roles works
- [x] Password reset mechanism works
- [ ] Application is deployed on Proxmox and accessible via IP
