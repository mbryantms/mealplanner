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
- [ ] Create `IngredientCategory` model (name, sort_order)
- [ ] Create `Ingredient` model (name, category FK, default_unit, notes)
- [ ] Create admin interface for IngredientCategory
- [ ] Create admin interface for Ingredient
- [ ] Add database migration

### Recipe System
- [ ] Create `Category` model (name, parent self-FK for hierarchy)
- [ ] Create `Tag` model (name, slug)
- [ ] Create `Recipe` model (all fields from spec)
- [ ] Create `RecipeIngredient` junction model
- [ ] Create Recipe-Tag many-to-many relationship
- [ ] Create admin interfaces for all recipe models
- [ ] Add database migrations

### Meal Planning System
- [ ] Create `MealType` enum (BREAKFAST, LUNCH, DINNER)
- [ ] Create `MealPlan` model (date, meal_type, recipe FK, custom_meal, servings_override, notes)
- [ ] Create admin interface for MealPlan
- [ ] Add database migration

### Shopping List System
- [ ] Create `ShoppingList` model (name, created_at, date_range)
- [ ] Create `ShoppingListItem` model (shopping_list FK, ingredient FK, custom_item, quantity, unit, checked)
- [ ] Create admin interfaces for shopping list models
- [ ] Add database migration

---

## Phase 2: Recipe Management

### Recipe CRUD
- [ ] Create recipe list view (with pagination)
- [ ] Create recipe detail view
- [ ] Create recipe create form
- [ ] Create recipe edit form
- [ ] Create recipe delete functionality
- [ ] Add URL routing for all recipe views

### Recipe Ingredients
- [ ] Create ingredient autocomplete endpoint (HTMX)
- [ ] Create inline ingredient add form
- [ ] Create on-the-fly ingredient creation modal/form
- [ ] Implement ingredient quantity/unit input
- [ ] Implement optional ingredient toggle
- [ ] Implement preparation notes field

### Recipe Organization
- [ ] Create category assignment UI
- [ ] Create tag assignment UI (multi-select)
- [ ] Create new category inline creation
- [ ] Create new tag inline creation

### Recipe Search & Filter
- [ ] Implement search by recipe name
- [ ] Implement filter by category
- [ ] Implement filter by tag
- [ ] Implement filter by ingredient
- [ ] Create combined search/filter UI
- [ ] Add HTMX live search functionality

### Recipe Scaling
- [ ] Implement serving size adjustment UI
- [ ] Calculate scaled ingredient quantities
- [ ] Display scaled quantities in recipe view

### Recipe Image (decision pending)
- [ ] Implement image upload field
- [ ] Configure media file storage
- [ ] Display recipe images in list/detail views
- [ ] Add image placeholder for recipes without images

---

## Phase 3: Meal Planning

### Weekly Calendar View
- [ ] Create week view template (Sunday-Saturday, 7-day grid)
- [ ] Display current week by default
- [ ] Show all 3 meal slots per day (Breakfast, Lunch, Dinner)
- [ ] Display assigned recipes in slots
- [ ] Display custom meals in slots

### Week Navigation
- [ ] Add previous/next week buttons
- [ ] Add "today" button to return to current week
- [ ] Implement week navigation via HTMX
- [ ] Display week date range in header

### Meal Assignment
- [ ] Create recipe picker/search for assignment
- [ ] Implement assign recipe to date/meal_type
- [ ] Create quick "Leftovers" option
- [ ] Create quick "Takeout" option
- [ ] Implement custom meal text entry
- [ ] Add servings override option
- [ ] Add notes field for meal instance

### Drag-and-Drop
- [ ] Implement drag-and-drop library integration
- [ ] Make meals draggable between slots
- [ ] Make meals draggable between days
- [ ] Handle drop validation and persistence
- [ ] Implement copy on drag with modifier key (optional)

### Meal Management
- [ ] Implement remove meal from slot
- [ ] Implement copy meal to another day

### Visual Indicators
- [ ] Show leftover-friendly meal indicator
- [ ] Show recipe image thumbnails (if available)
- [ ] Differentiate recipe vs custom meal styling

---

## Phase 4: Shopping Lists

### List Generation
- [ ] Create date range picker UI
- [ ] Implement "Generate from meal plan" function
- [ ] Aggregate ingredients across selected meals
- [ ] Handle duplicate ingredient combination (same units only for MVP)
- [ ] Group items by ingredient category
- [ ] Sort categories by sort_order

### List Display
- [ ] Create shopping list view
- [ ] Display items grouped by category
- [ ] Show quantity and unit for each item
- [ ] Display category headers/sections

### Item Check-off
- [ ] Implement checkbox for each item
- [ ] Persist checked state via HTMX
- [ ] Visual styling for checked items
- [ ] Option to hide/show checked items

### Custom Items
- [ ] Create "Add custom item" form
- [ ] Allow assigning custom items to categories
- [ ] Display custom items in appropriate sections

### List Management
- [ ] Create shopping list index (list of lists)
- [ ] Implement list rename
- [ ] Implement list delete
- [ ] Implement list duplicate/copy

### Mobile Optimization
- [ ] Optimize touch targets for check-off
- [ ] Ensure readable font sizes on mobile
- [ ] Test category collapse/expand on mobile
- [ ] Minimize data usage for in-store use

---

## Phase 5: User Interface

### Base Layout
- [ ] Create responsive base template
- [ ] Implement main navigation (Recipes, Plan, Shopping List)
- [ ] Add mobile hamburger menu
- [ ] Create consistent header/footer

### HTMX Integration
- [ ] Configure HTMX for all dynamic interactions
- [ ] Create partial templates for HTMX responses
- [ ] Implement loading indicators
- [ ] Handle HTMX errors gracefully

### Alpine.js Components
- [ ] Implement dropdown menus
- [ ] Implement modal dialogs
- [ ] Implement form validation feedback
- [ ] Implement toast notifications

### Tailwind Styling
- [ ] Define color palette/theme
- [ ] Create consistent button styles
- [ ] Create consistent form input styles
- [ ] Create consistent card/container styles

### Responsive Design
- [ ] Test and fix mobile layouts
- [ ] Test and fix tablet layouts
- [ ] Ensure touch-friendly interactions
- [ ] Test on actual mobile devices

---

## Phase 6: Authentication

### User System
- [ ] Configure Django auth settings
- [ ] Create custom User model (or extend) with role field
- [ ] Define Admin and User roles/permissions
- [ ] Create login page
- [ ] Create logout functionality
- [ ] Protect all views with login_required

### User Management
- [ ] Create user registration (admin-only creation for MVP)
- [ ] Create user profile page
- [ ] Implement password change
- [ ] Implement password reset (email-based)

### Permissions
- [ ] Implement admin-only views (user management, etc.)
- [ ] Ensure general users can CRUD recipes, meals, lists
- [ ] Test permission boundaries

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
- [ ] All data models are implemented and migrated
- [ ] Recipe CRUD with ingredients works fully
- [ ] Weekly meal planning calendar with drag-and-drop works
- [ ] Shopping list generation and check-off works
- [ ] Mobile-responsive UI is functional
- [ ] Authentication with admin/user roles works
- [ ] Password reset mechanism works
- [ ] Application is deployed on Proxmox and accessible via IP
