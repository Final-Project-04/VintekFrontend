from django import forms
import requests
from django.core.cache import cache


class ProductForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    brand = forms.CharField(max_length=50, required=False)
    model = forms.CharField(max_length=50, required=False)
    produced_year = forms.IntegerField(required=False)
    country_of_origin = forms.CharField(max_length=50, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    keywords = forms.CharField(max_length=1000, required=False)
    category = forms.ChoiceField(required=False)
    condition = forms.ChoiceField(required=True)
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    quantity = forms.IntegerField(required=True)
    image = forms.ImageField(required=False)
    
    
    CONDITION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Acceptable', 'Acceptable'),
        ('As-Is', 'As-Is'),
    ]
    condition = forms.ChoiceField(choices=CONDITION_CHOICES, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch categories and conditions from cache or API
        categories = cache.get('categories')
        conditions = cache.get('conditions')
        if not categories:
            response = requests.get('https://vintekapi.pythonanywhere.com/api/categories/')
            if response.status_code == 200:
                categories = response.json()
                cache.set('categories', categories)
        if not conditions:
            response = requests.get('https://vintekapi.pythonanywhere.com/api/product_conditions/')
            if response.status_code == 200:
                conditions = response.json()
                cache.set('conditions', conditions)
        # Populate the category and condition choices
        if categories:
            self.fields['category'].choices = [(category['id'], category['name']) for category in categories]
        if conditions:
            self.fields['condition'].choices = [(condition['id'], condition['name']) for condition in conditions]
            
            


from django import forms

class ReplyForm(forms.Form):
    recipient = forms.IntegerField()
    product = forms.IntegerField()
    message = forms.CharField(widget=forms.Textarea)
    original_message_id = forms.IntegerField()  