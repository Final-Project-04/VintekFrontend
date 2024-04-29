from django.shortcuts import render, redirect
from django.views import View
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
import requests
from .forms import PaymentMethodForm, CreditCardPaymentForm, PaypalPaymentForm, BankTransferPaymentForm


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        token = request.session.get('token')
        if token is None:
            return redirect('login')

        headers = {'Authorization': f'Token {token}'}
        user_id = request.session.get('user_id')
        response = requests.get(f'http://localhost:8000/api/users/{user_id}/', headers=headers)
        user = response.json()

        if user['adress'] is None:
            user['adress'] = 'No shipping address set.'

        return render(request, 'checkout.html', {'user': user})
    
    
    def post(self, request, *args, **kwargs):
        token = request.session.get('token')
        if token is None:
            return redirect('login')
        headers = {'Authorization': f'Token {token}'}

        # Get the user's shopping cart by making a GET request to the shopping cart API endpoint
        response = requests.get(f'http://localhost:8000/api/shopping-cart/', headers=headers)
        cart = response.json()

        # Calculate the total price of the cart
        total_price = sum(float(item['product']['price']) * int(item['quantity']) for item in cart['items'])

        # Get the user ID from the session
        user_id = request.session.get('user_id')

        # Create a new order by making a POST request to the order creation API endpoint
        data = {
            'user': user_id,
            'total_price': str(total_price),
            'shipping_address': request.POST.get('shipping_address'),
        }

        response = requests.post('http://localhost:8000/order/create/', headers=headers, json=data)

        # Check if the order was created successfully
        if response.status_code == 201:
            order = response.json()

            # Create an OrderProduct for each product in the cart
            for item in cart['items']:
                data = {
                    'order_id': order['id'],
                    'product_id': item['product']['id'],
                    'quantity': item['quantity'],
                    'price': item['product']['price'],
                }
                #print(f'Sending data: {data}')  # Print the data being sent
                response = requests.post('http://localhost:8000/order/product/add/', headers=headers, json=data)
                if response.status_code != 201:
                    print(f'Failed to create OrderProduct: {response.status_code} {response.content}')
                else:
                    order_product = response.json()
                    print(f'Successfully created OrderProduct: {order_product}')
        
             # Check if we have an order_id
            if order['id'] is None:
                print("No order_id")
            else:
                print("We have an order_id:", order['id'])

            ## Clear the shopping cart by making a DELETE request to the clear_cart API endpoint
            response = requests.delete('http://localhost:8000/api/shopping-cart/clear_cart/', headers=headers)

            # Check the response status code
            if response.status_code == 204:
                return redirect('order_and_payment:payment_with_order', order_id=order['id'])
            elif response.status_code == 404:
                return HttpResponse('Failed to clear shopping cart: Not Found', status=404)
            else:
                return HttpResponse('Failed to clear shopping cart: Unexpected status code', status=400)
        else:
            try:
                return render(request, 'checkout.html', {'error': 'There was an error processing your order.'})
            except Exception as e:
                return HttpResponse(f'An error occurred: {e}')
        

    
    
    
# Define a class OrderConfirmationView which inherits from Django's View class
class OrderConfirmationView(View):
    # Define the GET method for this view
    def get(self, request, *args, **kwargs):
        # Get the token from the session
        token = request.session.get('token')
        # Get the current user
        user = request.user

        # If the token is None, redirect to the login page
        if token is None:
            return redirect('login')

        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'}
        
        # Get the order_id from the URL parameters
        order_id = kwargs.get('order_id')

        # Send a GET request to the orders API to get the details of the order
        response = requests.get(f'http://localhost:8000/api/orders/{order_id}/', headers=headers)
        print(f'Response status code: {response.status_code}')

        # If the response status code is 200, get the order from the response and render the order_confirmation.html template with the order
        if response.status_code == 200:
            order = response.json()
            print(f'Order: {order}')
            return render(request, 'order_confirmation.html', {'order': order})
        # If the response status code is not 200, render the order_confirmation.html template with an error message
        else:
            return render(request, 'order_confirmation.html', {'error': 'There was an error retrieving your order.'})
        
        
#---------Payment Frontend---------------------------------------------------------------------------------------------------------------------------------

# Define a class PaymentView which inherits from Django's View class
class PaymentView(View):
    # Define the GET method for this view
    def get(self, request, order_id=None, *args, **kwargs):
        # Get the token from the session
        token = request.session.get('token')
        # If the token is None, redirect to the login page
        if token is None:
            return redirect('login')
        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'}
        # Get the payment method from the session, if it doesn't exist, default to None
        payment_method = request.session.get('payment_method', None)
        # If the payment method is None, create a PaymentMethodForm
        if payment_method is None:
            form = PaymentMethodForm()
        # If the payment method is 'credit_card', create a CreditCardPaymentForm
        elif payment_method == 'credit_card':
            form = CreditCardPaymentForm()
        # If the payment method is 'paypal', create a PaypalPaymentForm
        elif payment_method == 'paypal':
            form = PaypalPaymentForm()
        # If the payment method is 'bank_transfer', create a BankTransferPaymentForm
        elif payment_method == 'bank_transfer':
            form = BankTransferPaymentForm()
        # Render the payment.html template with the form
        return render(request, 'payment.html', {'form': form})

    # Define the POST method for this view
    def post(self, request, order_id=None, *args, **kwargs):
        # Get the token from the session
        token = request.session.get('token')
        # If the token is None, redirect to the login page
        if token is None:
            return redirect('login')
        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'}
        # Get the payment method from the session, if it doesn't exist, default to None
        payment_method = request.session.get('payment_method', None)
        # If 'payment_method' is in the POST data, create a PaymentMethodForm with the POST data
        if 'payment_method' in request.POST:
            form = PaymentMethodForm(request.POST)
            # If the form is valid, store the payment method in the session and redirect to the payment_with_order page
            if form.is_valid():
                request.session['payment_method'] = form.cleaned_data['payment_method']
                request.session.save()  # Save the session data immediately
                return redirect('order_and_payment:payment_with_order', order_id=order_id)
        # If 'payment_method' is not in the POST data, create a form based on the payment method
        else:
            if payment_method == 'credit_card':
                form = CreditCardPaymentForm(request.POST)
            elif payment_method == 'paypal':
                form = PaypalPaymentForm(request.POST)
            elif payment_method == 'bank_transfer':
                form = BankTransferPaymentForm(request.POST)
            else:
                return HttpResponse('Invalid payment method', status=400)
            # If the form is valid, store the payment info and remove the payment method from the session
            if form.is_valid():
                payment_info = form.cleaned_data
                payment_info['method'] = payment_method
                del request.session['payment_method']
                request.session.save()
            # If the form is not valid, render the payment.html template with the form
            else:
                return render(request, 'payment.html', {'form': form})
            # Define the data to be sent with the API request
            data = {
                'order_id': order_id,
                'payment_info': payment_info,
            }
            # Send a POST request to the payment process API and store the response
            response = requests.post('http://localhost:8000/payment/process/', headers=headers, json=data)
            # If the response status code is 200, redirect to the order_confirmation page
            if response.status_code == 200:
                return redirect('order_and_payment:order_confirmation', order_id=order_id)
            # If the response status code is not 200, render the payment.html template with an error message
            else:
                error_message = response.json().get('error', 'An error occurred')
                return render(request, 'payment.html', {'form': form, 'error_message': error_message})
        # If none of the above conditions are met, return a response with status code 400
        return HttpResponse('Invalid payment method', status=400)
    

from django.views import View
import requests

class MyOrdersView(View):
    template_name = 'my_orders.html'

    def get(self, request, *args, **kwargs):
        token = request.session.get('token')
        if token is None:
            return redirect('login')
        headers = {'Authorization': f'Token {token}'}
        
        # Fetch the orders made by the logged-in user
        response = requests.get('http://localhost:8000/api/orders', headers=headers)
        if response.status_code == 200:
            my_orders = response.json()
        else:
            my_orders = []

        # Fetch the orders sold by the logged-in user
        # This requires a new endpoint on the backend that lists orders where the logged-in user is the seller
        response = requests.get('http://localhost:8000/api/sold_orders', headers=headers)
        if response.status_code == 200:
            sold_orders = response.json()
        else:
            sold_orders = []

        return render(request, self.template_name, {'my_orders': my_orders, 'sold_orders': sold_orders})
    
    

class DeleteOrderView(View):
    def post(self, request, order_id, *args, **kwargs):
        token = request.session.get('token')
        if token is None:
            return redirect('login')
        headers = {'Authorization': f'Token {token}'}

        # Send a DELETE request to the API to delete the order
        response = requests.delete(f'http://localhost:8000/api/orders/{order_id}', headers=headers)
        if response.status_code == 204:
            # If the deletion was successful, redirect to the 'my_orders' page
            return redirect('order_and_payment:my_orders')
        else:
            # If the deletion failed, display an error message
            return render(request, 'error.html', {'message': 'Failed to delete order'})
