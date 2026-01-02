from django import forms
from django.forms import inlineformset_factory

from .models import Category, Ingredient, IngredientCategory, Recipe, RecipeIngredient, Tag


class RecipeForm(forms.ModelForm):
    """Form for creating and editing recipes."""

    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "instructions",
            "prep_time",
            "cook_time",
            "servings",
            "makes_leftovers",
            "leftover_days",
            "category",
            "tags",
            "source_url",
            "image",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Recipe name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 2,
                    "placeholder": "Brief description of the recipe",
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 10,
                    "placeholder": "Step-by-step instructions...",
                }
            ),
            "prep_time": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "mins",
                    "min": 0,
                }
            ),
            "cook_time": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "mins",
                    "min": 0,
                }
            ),
            "servings": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": 1,
                }
            ),
            "makes_leftovers": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 text-blue-600 rounded"}
            ),
            "leftover_days": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "days",
                    "min": 1,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "tags": forms.CheckboxSelectMultiple(
                attrs={"class": "space-y-2"}
            ),
            "source_url": forms.URLInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "https://...",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class RecipeIngredientForm(forms.ModelForm):
    """Form for recipe ingredients."""

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit", "preparation", "optional", "order"]
        widgets = {
            "ingredient": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-20 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "step": "0.001",
                    "min": "0",
                    "placeholder": "Qty",
                }
            ),
            "unit": forms.TextInput(
                attrs={
                    "class": "w-20 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "unit",
                }
            ),
            "preparation": forms.TextInput(
                attrs={
                    "class": "w-32 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "e.g. diced",
                }
            ),
            "optional": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 text-blue-600 rounded"}
            ),
            "order": forms.HiddenInput(),
        }


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True,
)


class IngredientQuickForm(forms.ModelForm):
    """Quick form for creating ingredients inline."""

    class Meta:
        model = Ingredient
        fields = ["name", "category", "default_unit"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ingredient name",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "default_unit": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "e.g. oz, cups, lbs",
                }
            ),
        }


class CategoryQuickForm(forms.ModelForm):
    """Quick form for creating categories inline."""

    class Meta:
        model = Category
        fields = ["name", "parent"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Category name",
                }
            ),
            "parent": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class TagQuickForm(forms.ModelForm):
    """Quick form for creating tags inline."""

    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Tag name",
                }
            ),
        }


class RecipeSearchForm(forms.Form):
    """Form for searching and filtering recipes."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Search recipes...",
                "hx-get": "",  # Will be set in template
                "hx-trigger": "keyup changed delay:300ms",
                "hx-target": "#recipe-list",
                "hx-push-url": "true",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(
            attrs={
                "class": "px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "hx-get": "",
                "hx-trigger": "change",
                "hx-target": "#recipe-list",
                "hx-include": "[name='q'], [name='tag']",
                "hx-push-url": "true",
            }
        ),
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(
            attrs={
                "class": "px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "hx-get": "",
                "hx-trigger": "change",
                "hx-target": "#recipe-list",
                "hx-include": "[name='q'], [name='category']",
                "hx-push-url": "true",
            }
        ),
    )
