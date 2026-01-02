from django import forms

from apps.recipes.models import Recipe

from .models import MealPlan, MealType


class MealPlanForm(forms.ModelForm):
    """Form for creating and editing meal plans."""

    class Meta:
        model = MealPlan
        fields = ["date", "meal_type", "recipe", "custom_meal", "servings_override", "notes"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "meal_type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "recipe": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "custom_meal": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "e.g., Takeout, Leftovers, Eating out...",
                }
            ),
            "servings_override": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": 1,
                    "placeholder": "Servings",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 2,
                    "placeholder": "Optional notes for this meal...",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        recipe = cleaned_data.get("recipe")
        custom_meal = cleaned_data.get("custom_meal")

        if not recipe and not custom_meal:
            raise forms.ValidationError(
                "Please select a recipe or enter a custom meal."
            )

        return cleaned_data


class QuickMealForm(forms.Form):
    """Quick form for adding meals from the calendar view."""

    date = forms.DateField(widget=forms.HiddenInput())
    meal_type = forms.ChoiceField(
        choices=MealType.choices,
        widget=forms.HiddenInput(),
    )
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            }
        ),
    )
    custom_meal = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Or enter custom meal...",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        recipe = cleaned_data.get("recipe")
        custom_meal = cleaned_data.get("custom_meal")

        if not recipe and not custom_meal:
            raise forms.ValidationError(
                "Please select a recipe or enter a custom meal."
            )

        return cleaned_data


class MealMoveForm(forms.Form):
    """Form for moving a meal to a different date/slot."""

    new_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            }
        )
    )
    new_meal_type = forms.ChoiceField(
        choices=MealType.choices,
        widget=forms.Select(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            }
        ),
    )
