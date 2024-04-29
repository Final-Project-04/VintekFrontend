# Importing necessary modules from Django and other libraries
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.views import View
import requests
import json

# Define a class ShoppingCartView which inherits from Django's View class
class ShoppingCartView(View):
    # Define a method to get headers for requests
    def get_headers(self, request):
        # Get the token from the session
        token = request.session.get('token')
        # Return the headers with the token if it exists, else return an empty dictionary
        return {'Authorization': f'Token {token}'} if token else {}
        
    # Define the GET method for this view
    def get(self, request):
        # Get the headers
        headers = self.get_headers(request)
        # Send a GET request to the shopping cart API and store the response
        response = requests.get('http://localhost:8000/api/shopping-cart/', headers=headers)
        # Convert the response to JSON
        cart = response.json()
        # Get the items from the cart, if there are no items, return an empty list
        items = cart.get('items', [])
        # Initialize total price to 0
        total_price = 0
        # Iterate over each item in the cart
        for item in items:
            # If the product has an image, prepend the server URL to the image URL
            if item['product']['image'] is not None:
                item['product']['image'] = 'http://localhost:8000' + item['product']['image']
            # Calculate the total price for this item (price * quantity) and add it to the total price
            item_total = float(item['product']['price']) * float(item['quantity'])
            total_price += item_total
            # Store the item total in the item dictionary
            item['item_total'] = item_total
        # Render the cart.html template with the items and total price
        return render(request, 'cart.html', {'items': items, 'total_price': total_price})
    
# Define a class AddProductView which inherits from ShoppingCartView
class AddProductView(ShoppingCartView):
    # Define the POST method for this view
    def post(self, request, product_id):
        # Get the quantity from the POST data, if it doesn't exist, default to 1
        quantity = int(request.POST.get('quantity', 1))
        # Get the headers
        headers = self.get_headers(request)
        # Define the URL for the API request
        url = f'http://localhost:8000/api/shopping-cart/add-product/'
        # Define the data to be sent with the request
        data = {'product_id': product_id, 'quantity': quantity}
        # Send a POST request to the API and store the response
        response = requests.post(url, headers=headers, data=data)
        # Try to get the message from the response, if it fails, store an error message
        try:
            message = response.json().get('message')
        except json.JSONDecodeError:
            message = f"Invalid JSON in response: {response.content}"
        # Add a success message to the Django messages framework
        messages.success(request, message)
        # Redirect to the shopping cart page
        return HttpResponseRedirect(reverse('shoppingcart:cart'))
    
# Define a class RemoveProductView which inherits from ShoppingCartView
class RemoveProductView(ShoppingCartView):
    # Define the POST method for this view
    def post(self, request, cart_item_id):
        # Get the headers
        headers = self.get_headers(request)
        # Send a DELETE request to the API to remove a product and store the response
        response = requests.delete(f'http://localhost:8000/api/shopping-cart/{cart_item_id}/remove-product/', headers=headers)
        # If the response has content, get the message from it, else store a default message
        if response.content:
            message = response.json().get('message')
        else:
            message = "No content in response"
        # Redirect to the shopping cart page
        return redirect('shoppingcart:cart')

# Define a class DeleteProductView which inherits from ShoppingCartView
class DeleteProductView(ShoppingCartView):
    # Define the POST method for this view
    def post(self, request, cart_item_id):
        # Get the headers
        headers = self.get_headers(request)
        # Send a DELETE request to the API to delete a product and store the response
        response = requests.delete(f'http://localhost:8000/api/shopping-cart/{cart_item_id}/delete-product/', headers=headers)
        # If the response has content, get the message from it, else store a default message
        if response.content:
            message = response.json().get('message')
        else:
            message = "No content in response"
        # Redirect to the shopping cart page
        return redirect('shoppingcart:cart')

# Define a class UpdateQuantityView which inherits from ShoppingCartView
class UpdateQuantityView(ShoppingCartView):
    # Define the POST method for this view
    def post(self, request, pk):
        # Get the change in quantity from the POST data, if it doesn't exist, default to 0
        change = int(request.POST.get('change', 0))
        # Get the headers
        headers = self.get_headers(request)
        # If the change is negative, send a DELETE request to decrease the quantity
        if change < 0:
            response = requests.delete(f'http://localhost:8000/api/shopping-cart/{pk}/remove-product/', headers=headers)
        # If the change is positive, send a POST request to increase the quantity
        else:
            response = requests.post(f'http://localhost:8000/api/shopping-cart/{pk}/increment-product/', headers=headers)
        # If the response status code is 200 or 204, add a success message, else add an error message
        if response.status_code == 200 or response.status_code == 204:
            messages.success(request, "Quantity updated successfully")
        else:
            messages.error(request, "Maximum quantity reached")
        # Redirect to the shopping cart page
        return redirect('shoppingcart:cart')
    
# Define a class ShoppingCartCalculator
class ShoppingCartCalculator:
    # Define a static method to calculate the total price of the cart
    @staticmethod
    def calculate_totals(cart):
        # Get the items from the cart, if there are no items, return an empty list
        items = cart.get('items', [])
        # Initialize total price to 0
        total_price = 0
        # Iterate over each item in the cart
        for item in items:
            # If the product has an image, prepend the server URL to the image URL
            if item['product']['image'] is not None:
                item['product']['image'] = 'http://localhost:8000' + item['product']['image']
            # Try to convert the price and quantity to float and calculate the item total
            try:
                price = float(item['product']['price'])
                quantity = float(item['quantity'])
            # If the conversion fails, skip this item
            except ValueError:
                continue
            # Calculate the item total and add it to the total price
            item_total = price * quantity
            total_price += item_total
            # Store the item total in the item dictionary
            item['item_total'] = item_total
        # Return the items and total price
        return items, total_price