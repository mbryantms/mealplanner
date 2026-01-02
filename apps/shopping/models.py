from django.db import models


class ShoppingList(models.Model):
    """Generated or manual shopping list."""

    name = models.CharField(max_length=200, help_text="List name (e.g., 'Week of Jan 6')")
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(
        null=True, blank=True, help_text="Start date if generated from meal plan"
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="End date if generated from meal plan"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def date_range(self):
        """Return formatted date range if both dates are set."""
        if self.start_date and self.end_date:
            return f"{self.start_date} to {self.end_date}"
        return None

    @property
    def checked_count(self):
        """Return count of checked items."""
        return self.items.filter(checked=True).count()

    @property
    def total_count(self):
        """Return total item count."""
        return self.items.count()

    @property
    def progress_percent(self):
        """Return completion percentage."""
        total = self.total_count
        if total == 0:
            return 0
        return int((self.checked_count / total) * 100)


class ShoppingListItem(models.Model):
    """An item on a shopping list."""

    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    ingredient = models.ForeignKey(
        "recipes.Ingredient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopping_list_items",
        help_text="Ingredient from master list (blank for custom items)",
    )
    custom_item = models.CharField(
        max_length=200, blank=True, help_text="Text for non-ingredient items"
    )
    quantity = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit = models.CharField(max_length=50, blank=True)
    checked = models.BooleanField(default=False)
    category_override = models.ForeignKey(
        "recipes.IngredientCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopping_list_items",
        help_text="Override category for custom items",
    )

    class Meta:
        ordering = ["ingredient__category__sort_order", "ingredient__name", "custom_item"]

    def __str__(self):
        name = self.ingredient.name if self.ingredient else self.custom_item
        if self.quantity:
            return f"{self.quantity} {self.unit} {name}".strip()
        return name

    @property
    def display_name(self):
        """Return the item name for display."""
        return self.ingredient.name if self.ingredient else self.custom_item

    @property
    def category(self):
        """Return the category for grouping (ingredient's or override)."""
        if self.category_override:
            return self.category_override
        if self.ingredient and self.ingredient.category:
            return self.ingredient.category
        return None
