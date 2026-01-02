from django.db import models


class MealType(models.TextChoices):
    """Enum for meal types."""

    BREAKFAST = "breakfast", "Breakfast"
    LUNCH = "lunch", "Lunch"
    DINNER = "dinner", "Dinner"


class MealPlan(models.Model):
    """A scheduled meal assignment."""

    date = models.DateField()
    meal_type = models.CharField(
        max_length=20, choices=MealType.choices, default=MealType.DINNER
    )
    recipe = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meal_plans",
        help_text="Recipe for this meal (leave blank for custom meals)",
    )
    custom_meal = models.CharField(
        max_length=200,
        blank=True,
        help_text="Text for non-recipe meals (e.g., 'Takeout', 'Leftovers')",
    )
    servings_override = models.PositiveIntegerField(
        null=True, blank=True, help_text="Override the recipe's default serving count"
    )
    notes = models.TextField(blank=True, help_text="Notes for this specific meal")

    class Meta:
        ordering = ["date", "meal_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "meal_type"], name="unique_meal_per_slot"
            )
        ]

    def __str__(self):
        meal_name = self.recipe.name if self.recipe else self.custom_meal or "Empty"
        return f"{self.date} {self.get_meal_type_display()}: {meal_name}"

    @property
    def servings(self):
        """Return the effective serving count."""
        if self.servings_override:
            return self.servings_override
        if self.recipe:
            return self.recipe.servings
        return None

    @property
    def is_recipe(self):
        """Check if this meal is a recipe (vs custom meal)."""
        return self.recipe is not None

    @property
    def is_leftovers(self):
        """Check if this is marked as leftovers."""
        return self.custom_meal.lower() == "leftovers" if self.custom_meal else False

    @property
    def is_takeout(self):
        """Check if this is marked as takeout."""
        return self.custom_meal.lower() == "takeout" if self.custom_meal else False
