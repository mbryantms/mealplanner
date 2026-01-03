from django import forms

from apps.recipes.models import Ingredient

from .models import ShoppingList, ShoppingListItem


class ShoppingListForm(forms.ModelForm):
    """Form for creating/editing shopping lists."""

    class Meta:
        model = ShoppingList
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "e.g., Week of Jan 6",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class GenerateFromMealPlanForm(forms.Form):
    """Form for generating a shopping list from meal plan date range."""

    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Shopping list name",
            }
        ),
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            }
        )
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date must be after start date.")

        return cleaned_data


class ShoppingListItemForm(forms.ModelForm):
    """Form for adding/editing shopping list items."""

    class Meta:
        model = ShoppingListItem
        fields = ["ingredient", "custom_item", "quantity", "unit"]
        widgets = {
            "ingredient": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "custom_item": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Or enter custom item...",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Qty",
                }
            ),
            "unit": forms.TextInput(
                attrs={
                    "class": "w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "unit",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        ingredient = cleaned_data.get("ingredient")
        custom_item = cleaned_data.get("custom_item")

        if not ingredient and not custom_item:
            raise forms.ValidationError(
                "Please select an ingredient or enter a custom item."
            )

        return cleaned_data


class QuickItemForm(forms.Form):
    """Quick form for adding items via HTMX."""

    item_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "flex-grow px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Add item...",
            }
        ),
    )
    quantity = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "step": "0.01",
                "min": "0",
                "placeholder": "Qty",
            }
        ),
    )
    unit = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "unit",
            }
        ),
    )
