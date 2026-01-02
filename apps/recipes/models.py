from django.db import models
from django.utils.text import slugify


class IngredientCategory(models.Model):
    """Groups ingredients by store section for organized shopping lists."""

    name = models.CharField(max_length=100, unique=True)
    sort_order = models.PositiveIntegerField(
        default=0, help_text="Display order for shopping list organization"
    )

    class Meta:
        verbose_name_plural = "Ingredient categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """A canonical ingredient used across all recipes."""

    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(
        IngredientCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ingredients",
    )
    default_unit = models.CharField(
        max_length=50,
        blank=True,
        help_text="Default measurement unit (oz, lb, cups, etc.)",
    )
    notes = models.TextField(
        blank=True, help_text="Optional notes (e.g., 'boneless skinless preferred')"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """Hierarchical grouping for recipes (e.g., Cuisine > Italian > Pasta)."""

    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "parent"], name="unique_category_name_per_parent"
            )
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class Tag(models.Model):
    """Flat labels for flexible filtering (e.g., 'Quick', 'Kid-Friendly')."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """A meal that can be prepared and scheduled."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Brief description")
    instructions = models.TextField(blank=True, help_text="Preparation steps")
    prep_time = models.PositiveIntegerField(
        null=True, blank=True, help_text="Time in minutes for preparation"
    )
    cook_time = models.PositiveIntegerField(
        null=True, blank=True, help_text="Time in minutes for cooking"
    )
    servings = models.PositiveIntegerField(default=4, help_text="Default serving count")
    makes_leftovers = models.BooleanField(default=False)
    leftover_days = models.PositiveIntegerField(
        null=True, blank=True, help_text="How many days leftovers typically last"
    )
    source_url = models.URLField(
        blank=True, help_text="Original recipe URL (for reference)"
    )
    image = models.ImageField(upload_to="recipes/", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="recipes")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_time(self):
        """Calculate total time from prep and cook time."""
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook if prep or cook else None


class RecipeIngredient(models.Model):
    """Links recipes to ingredients with quantities."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    quantity = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit = models.CharField(
        max_length=50, blank=True, help_text="Unit override (or use ingredient default)"
    )
    preparation = models.CharField(
        max_length=100, blank=True, help_text="Optional modifier (e.g., 'diced')"
    )
    optional = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order in recipe")

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_ingredient_per_recipe"
            )
        ]

    def __str__(self):
        parts = []
        if self.quantity:
            parts.append(str(self.quantity))
        if self.unit:
            parts.append(self.unit)
        elif self.ingredient.default_unit:
            parts.append(self.ingredient.default_unit)
        parts.append(self.ingredient.name)
        if self.preparation:
            parts.append(f"({self.preparation})")
        if self.optional:
            parts.append("[optional]")
        return " ".join(parts)
