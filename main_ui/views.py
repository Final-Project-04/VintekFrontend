import requests
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import  HeroImage
import random
from django.views import View
from django.http import JsonResponse
from .forms import ProductForm
from requests_toolbelt.multipart.encoder import MultipartEncoder
from django.views.generic.edit import FormView
from .forms import ReplyForm
from django.contrib import messages
from dateutil.parser import parse

# Define a class Home which inherits from Django's TemplateView
class Home(TemplateView):
    # Define the template name for this view
    template_name = 'home.html'

    # Override the get_context_data method to add additional context
    def get_context_data(self, **kwargs):
        # Call the superclass's get_context_data method
        context = super().get_context_data(**kwargs)
        # Get all HeroImage objects and convert them to a list
        images = list(HeroImage.objects.all())
        # Shuffle the list of images
        random.shuffle(images)
        # Add the shuffled images to the context
        context['images'] = images

        # Get the user_id from the session
        user_id = self.request.session.get('user_id')
        # Add the user_id to the context
        context['user_id'] = user_id

        # Return the context
        return context
    
# -----------------Categories-------------------------------------------------------------------------------------------------------------------------------

# Define a class Categories which inherits from Django's TemplateView
class Categories(TemplateView):
    # Define the template name for this view
    template_name = 'categories.html'

    # Override the get_context_data method to add additional context
    def get_context_data(self, **kwargs):
        # Call the superclass's get_context_data method
        context = super().get_context_data(**kwargs)
        # Send a GET request to the categories API
        response = requests.get('https://vintekapi.pythonanywhere.com/api/categories/')

        # Try to convert the response to JSON, if it fails, set categories_data to an empty list
        try:
            categories_data = response.json()
        except ValueError:
            categories_data = []

        # Iterate over each category in categories_data
        for category in categories_data:
            # Send a GET request to the products API for this category
            response = requests.get(f'https://vintekapi.pythonanywhere.com/api/categories/{category["id"]}/products/')
            # If the response status code is 404, set the products for this category to an empty list and continue to the next category
            if response.status_code == 404:
                category['products'] = []
                continue
            # Try to convert the response to JSON and add the products to the category
            try:
                products = response.json()
                # For each product, build the absolute URL for the product detail page and add it to the product
                for product in products:
                    product['detail_url'] = self.request.build_absolute_uri(reverse('product_detail', kwargs={'product_id': product['id']}))
                # Add the products to the category
                category['products'] = products
            # If the conversion to JSON fails, set the products for this category to an empty list
            except ValueError:
                category['products'] = []

        # Add the categories to the context
        context['categories'] = categories_data
        # Return the context
        return context
    
# -----------------User Data Functions-------------------------------------------------------------------------------------------------------------------------------


# Define a function get_username which takes a user_id and a token as parameters
def get_username(user_id, token):
    # If the token exists, define the headers for the API request with the token, else define an empty dictionary
    headers = {'Authorization': f'Token {token}'} if token else {}
    # Send a GET request to the user API with the user_id and headers, and store the response
    response = requests.get(f'https://vintekapi.pythonanywhere.com/user/{user_id}/', headers=headers)
    # If the response status code is 200, convert the response to JSON, get the username from the user and return it
    if response.status_code == 200:
        user = response.json()
        return user['username']
    # If the response status code is not 200, return None
    else:
        return None


# -----------All products-----------------------------------------------------------------------------------------------------------------------

# Define a class ProductListView which inherits from Django's TemplateView
class ProductListView(TemplateView):
    # Define the template name for this view
    template_name = 'product_list.html'

    # Override the get_context_data method to add additional context
    def get_context_data(self, **kwargs):
        # Call the superclass's get_context_data method
        context = super().get_context_data(**kwargs)

        # Define the URL for the products API
        api_url = 'https://vintekapi.pythonanywhere.com/api/products'
        try:
            # Send a GET request to the products API and store the response
            response = requests.get(api_url)
            # Raise an exception if the response status code is not 200
            response.raise_for_status() 
            # Convert the response to JSON and store the products
            products = response.json()

            # Initialize an empty list for valid products
            valid_products = []
            # Iterate over each product in products
            for product in products:
                # If the product has an 'id' key, build the absolute URL for the product detail page, add it to the product, and add the product to valid_products
                if 'id' in product:
                    product['detail_url'] = reverse('product_detail', kwargs={'product_id': product['id']})
                    valid_products.append(product)

            # Add the valid products to the context
            context['products'] = valid_products

        # If a requests.RequestException is raised, print an error message and add an error message to the context
        except requests.RequestException as e:
            print(f"Error accessing API: {e}")
            context['error_message'] = "Failed to retrieve product data from the API."

        # If a KeyError is raised, print an error message and add an error message to the context
        except KeyError as e:
            # Handle missing keys in product data
            print(f"Missing key in product data: {e}")
            context['error_message'] = "Product data format is invalid."

        # Return the context
        return context


# -----------------Product Create-------------------------------------------------------------------------------------------------------------------------------

# Define a class ProductCreateView which inherits from Django's FormView
class ProductCreateView(FormView):
    # Define the template name for this view
    template_name = 'product_create.html'
    # Define the form class for this view
    form_class = ProductForm

    # Override the form_valid method to add additional validation
    def form_valid(self, form):
        # Get the user_id and token from the session
        user_id = self.request.session.get('user_id')
        token = None
        if user_id:
            token = self.request.session.get('token')

        # If the token is None, add an error to the form and return form_invalid
        if token is None:
            form.add_error(None, 'User is not logged in')
            return self.form_invalid(form)

        # Get the image file from the request files
        image_file = self.request.FILES.get('image')
        # If the image file exists, store the image data, else store None
        image_data = (image_file.name, image_file, image_file.content_type) if image_file else None

        # Define the data to be sent with the API request
        data = MultipartEncoder(
            fields={
                'name': form.cleaned_data.get('name'),
                'brand': form.cleaned_data.get('brand'),
                'model': form.cleaned_data.get('model'),
                'produced_year': str(form.cleaned_data.get('produced_year')), 
                'country_of_origin': form.cleaned_data.get('country_of_origin'),
                'description': form.cleaned_data.get('description'),
                'keywords': form.cleaned_data.get('keywords'),
                'category': str(form.cleaned_data.get('category')),  
                'condition': form.cleaned_data.get('condition'),
                'price': str(form.cleaned_data.get('price')),  
                'quantity': str(form.cleaned_data.get('quantity')),  
                'image': image_data,
                'user': str(user_id) 
            }
        )
        

        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}', 'Content-Type': data.content_type}
        # Send a POST request to the product creation API and store the response
        response = requests.post('https://vintekapi.pythonanywhere.com/api/products/create/', data=data, headers=headers)

        # If the response status code is 201, redirect to the products page
        if response.status_code == 201:
            return redirect('products')
        # If the response status code is not 201, add an error to the form and return form_invalid
        else:
            form.add_error(None, 'Unable to create product')
            return self.form_invalid(form)
        

# -----------------Product Detail-------------------------------------------------------------------------------------------------------------------------------
# Define a class ProductDetailView which inherits from Django's TemplateView
class ProductDetailView(TemplateView):
    # Define the template name for this view
    template_name = 'product_detail.html'

    # Override the get_context_data method to add additional context
    def get_context_data(self, **kwargs):
        # Call the superclass's get_context_data method
        context = super().get_context_data(**kwargs)
        # Get the product_id from the URL parameters
        product_id = kwargs.get('product_id')
        # Get the token from the session
        token = self.request.session.get('token')
        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'} if token else {}
        # Send a GET request to the products API with the product_id and headers, and store the response
        response = requests.get(f'https://vintekapi.pythonanywhere.com/api/products/{product_id}', headers=headers)
        # If the response status code is 200, convert the response to JSON, get the product, and add additional data to the product
        if response.status_code == 200:
            product = response.json()
            # Get the user_id from the session
            user_id = self.request.session.get('user_id')
            # If the user_id exists, check if the user is the owner of the product and add the result to the product
            if user_id:
                product['is_owner'] = user_id == product['user']
            # Get the username of the user who owns the product and add it to the product
            product['username'] = get_username(product['user'], token)  # Passing the token to the get_username function
            # Add the product to the context
            context['product'] = product
        # Return the context
        return context


# -----------------Product Edit-------------------------------------------------------------------------------------------------------------------------------

# Define a class ProductEditView which inherits from Django's View class
class ProductEditView(View):
    # Define the template name for this view
    template_name = 'product_edit.html'

    # Define the GET method for this view
    def get(self, request, *args, **kwargs):
        # Get the product_id from the URL parameters
        product_id = kwargs.get('product_id')
        # Send a GET request to the products API with the product_id and store the response
        response = requests.get(f'https://vintekapi.pythonanywhere.com/api/products/{product_id}')
        # Convert the response to JSON and store the product
        product = response.json()
        # Render the product_edit.html template with the product
        return render(request, self.template_name, {'product': product})

    # Define the POST method for this view
    def post(self, request, *args, **kwargs):
        # Get the user_id from the session
        user_id = request.session.get('user_id')
        # If the user_id exists, get the token from the session, get the product_id from the URL parameters, and define the data to be sent with the API request
        if user_id:
            token = request.session.get('token')
            product_id = kwargs.get('product_id')
            data = {
                'name': request.POST.get('name'),
                'brand': request.POST.get('brand'),
                'model': request.POST.get('model'),
                'produced_year': request.POST.get('produced_year'),
                'country_of_origin': request.POST.get('country_of_origin'),
                'category': request.POST.get('category'),
                'price': request.POST.get('price'),
                'description': request.POST.get('description'),
                'image': request.FILES.get('image'),
                'color': request.POST.get('color'),
                'quantity': request.POST.get('quantity'),
                'user': user_id,
            }
            # Send a PUT request to the product API with the product_id, data, and headers, and store the response
            response = requests.put(f'https://vintekapi.pythonanywhere.com/api/products/{product_id}/', data=data, headers={'Authorization': f'Token {token}'})
            # If the response status code is 200, redirect to the product_detail page with the product_id
            if response.status_code == 200:
                return redirect('product_detail', product_id=product_id)
            # If the response status code is not 200, return a JsonResponse with an error message and status code 400
            else:
                return JsonResponse({'error': 'An error occurred while trying to update product data'}, status=400)
        # If the user_id does not exist, return a JsonResponse with an error message and status code 400
        return JsonResponse({'error': 'An error occurred'}, status=400)


# -----------------Product List_By_Category-------------------------------------------------------------------------------------------------------------------------------

# Define a class ProductListByCategoryView which inherits from Django's TemplateView
class ProductListByCategoryView(TemplateView):
    # Define the template name for this view
    template_name = 'category_list_products.html'

    # Override the get_context_data method to add additional context
    def get_context_data(self, **kwargs):
        # Call the superclass's get_context_data method
        context = super().get_context_data(**kwargs)
        # Get the category_id from the URL parameters
        category_id = self.kwargs['category_id']
        # Send a GET request to the products API with the category_id as a query parameter and store the response
        response = requests.get(
            f'https://vintekapi.pythonanywhere.com/api/products/?category={category_id}')
        # Convert the response to JSON and store the products
        products = response.json()
        # Add the products to the context
        context['products'] = products
        # Return the context
        return context


# -----------------Product Delete-------------------------------------------------------------------------------------------------------------------------------
# Define a class ProductDeleteView which inherits from Django's View class
class ProductDeleteView(View):
    # Define the POST method for this view
    def post(self, request, *args, **kwargs):
        # Get the product_id from the URL parameters
        product_id = kwargs.get("product_id")
        # Get the token from the session
        token = request.session.get("token")
        # Define the headers for the API request
        headers = {"Authorization": f"Token {token}"} if token else {}

        # Add an info message to the request
        messages.info(request, "Attempting to delete product...")

        # Send a DELETE request to the products API with the product_id and headers, and store the response
        response = requests.delete(
            f"https://vintekapi.pythonanywhere.com/api/products/{product_id}", headers=headers
        )
        # If the response status code is 204, add a success message to the request and redirect to the products page
        if response.status_code == 204:
            messages.success(request, "Product deleted successfully.")
            return redirect("products")
        # If the response status code is not 204, return a JsonResponse with an error message and status code 400
        else:
            return JsonResponse(
                {"error": "An error occurred while trying to delete the product"},
                status=400,
            )
        

# -----------Search-------------------------------------------------------------------------------------------------------------------------------

class SearchView(TemplateView):
    template_name = 'product_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = self.request.GET.get('query', '')

        response = requests.get(
            f'https://vintekapi.pythonanywhere.com/api/products/search/?search={search_term}')

        try:
            products = response.json()
            if not isinstance(products, list):
                raise ValueError
        except ValueError:
            products = []

        if not products:
            context['error'] = 'No products found for your search. Please try a different search term.'
        else:
            for product in products:
                product['url'] = reverse('product_detail', kwargs={'product_id': product['id']})
            context['products'] = products

        return context
#---------Wishlist-------------------------------------------------------------------------------------------------------------------------------

# Define a class WishlistView which inherits from Django's View class
class WishlistView(View):
    # Define the GET method for this view
    def get(self, request, *args, **kwargs):
        # Get the token from the session
        token = request.session.get('token')
        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'} if token else {}
        # Send a GET request to the wishlist API with the headers and store the response
        response = requests.get('https://vintekapi.pythonanywhere.com/api/wishlist/', headers=headers)
        # Convert the response to JSON and store the wishlist
        wishlist = response.json()
        
        # Iterate over each product in the wishlist
        for product in wishlist:
            # Prepend the domain of the API server to the image URL and update the image URL in the product
            product['image'] = 'https://vintekapi.pythonanywhere.com/' + product['image']
                
        # Render the wishlist.html template with the wishlist
        return render(request, 'wishlist.html', {'wishlist': wishlist})

    # Define the POST method for this view
    def post(self, request, *args, **kwargs):
        # Get the product_id and action from the POST parameters
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        # Get the token from the session
        token = request.session.get('token')
        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'} if token else {}

        # If the action is 'delete', send a DELETE request to the wishlist API with the product_id and headers, and store the response
        if action == 'delete':
            response = requests.delete('https://vintekapi.pythonanywhere.com/api/wishlist/', data={'product_id': product_id}, headers=headers)
            # If the response status code is 204, redirect to the wishlist page
            if response.status_code == 204:
                return redirect('wishlist')
            # If the response status code is not 204, render the wishlist.html template with an error message
            else:
                error_message = f"An error occurred while trying to remove product from wishlist: {response.status_code} {response.text}"
                return render(request, 'wishlist.html', {'error': error_message})
        # If the action is not 'delete', send a POST request to the wishlist API with the product_id and headers, and store the response
        else:
            response = requests.post('https://vintekapi.pythonanywhere.com/api/wishlist/', data={'product_id': product_id}, headers=headers)
            # If the response status code is 204, redirect to the wishlist page
            if response.status_code == 204:
                return redirect('wishlist')
            # If the response status code is not 204, render the wishlist.html template with an error message
            else:
                return render(request, 'wishlist.html', {'error': 'An error occurred while trying to add product to wishlist'})
            
# -----------------Mesage Sller-------------------------------------------------------------------------------------------------------------------------------

# Define a class MessageFormView which inherits from Django's View class
class MessageFormView(View):
    # Define the GET method for this view
    def get(self, request, *args, **kwargs):
        # Retrieve user_id and username from the session
        user_id = request.session.get('user_id')
        user_name = request.session.get('username')

        # Retrieve product_id from the URL parameters
        product_id = kwargs['product_id']

        # Retrieve token from the session and prepare headers for the API request
        token = request.session.get('token')
        headers = {'Authorization': f'Token {token}'} if token else {}

        # Send a GET request to the products API with the product_id and headers
        response = requests.get(f'https://vintekapi.pythonanywhere.com/api/products/{product_id}/', headers=headers)

        # If the response status code is 200, process the product data
        if response.status_code == 200:
            # Convert the response to JSON and store the product
            product = response.json()

            # Retrieve the seller_id from the product data
            seller_id = product["user"]

            # Retrieve the seller_name using the get_username function
            seller_name = get_username(seller_id, token)

            # Add an info message to the request
            messages.info(request, f'Name: {seller_name}')

            # Prepare the context for the template
            context = {
                'user_id': user_id,
                'user_name': user_name,
                'product_id': product["id"],
                'product_name': product["name"],
                'seller_id': seller_id,
                'seller_name': seller_name,
            }

            # Redirect to the product_detail page with the product_id
            return redirect('product_detail', product_id=product["id"])

        # If the response status code is not 200, redirect to the product_detail page with the product_id
        else:
            return redirect('product_detail', product_id=product["id"])

    # Define the POST method for this view
    def post(self, request, *args, **kwargs):
        # Retrieve sender, recipient, product, and message from the POST parameters
        sender = request.POST.get('sender')
        recipient = request.POST.get('recipient')
        product = request.POST.get('product')
        message = request.POST.get('message')

        # Retrieve token from the session and prepare headers for the API request
        token = request.session.get('token')
        headers = {'Authorization': f'Token {token}'} if token else {}

        # Prepare the message data for the API request
        message_data = {
            'sender': sender,
            'recipient': recipient,
            'product': product,
            'message': message,
        }

        # Send a POST request to the messages API with the message_data and headers
        response = requests.post('https://vintekapi.pythonanywhere.com/messages/', data=message_data, headers=headers)

        # If the response status code is 201, add a success message to the request and redirect to the product_detail page with the product_id
        if response.status_code == 201:
            messages.success(request, 'Message sent successfully')
            return redirect('product_detail', product_id=product)

        # If the response status code is not 201, add an error message to the request and redirect to the product_detail page with the product_id
        else:
            messages.error(request, 'Failed to send message')
            return redirect('product_detail', product_id=product)
        
        
        
# Define a class UserMessagesView which inherits from Django's TemplateView
class UserMessagesView(TemplateView):
    # Define the template name for this view
    template_name = 'user_messages.html'

    # Override the get_context_data method to add additional context
    def get_context_data(self, **kwargs):
        # Call the superclass's get_context_data method
        context = super().get_context_data(**kwargs)
        # Add a ReplyForm instance to the context
        context['form'] = ReplyForm()

        # Get the user_id and token from the session
        user_id = self.request.session.get('user_id')
        token = self.request.session.get('token')

        # Define the headers for the API request
        headers = {'Authorization': f'Token {token}'} if token else {}

        # Send a GET request to the messages API with the user_id as a query parameter and headers, and store the response
        response = requests.get(f'https://vintekapi.pythonanywhere.com/messages/?user_id={user_id}', headers=headers)

        # If the response status code is 200, convert the response to JSON and store the messages, else store an empty list
        messages = response.json() if response.status_code == 200 else []

        # Sort the messages by timestamp in descending order
        messages.sort(key=lambda message: parse(message['timestamp']), reverse=True)

        # Iterate over each message in messages
        for message in messages:
            # Store the sender_id, recipient_id, product_id, original_message_id, and timestamp in the message
            message['sender_id'] = message['sender']
            message['recipient_id'] = message['recipient']
            message['product_id'] = message['product']
            message['original_message_id'] = message['id']
            message['timestamp'] = parse(message['timestamp'])

            # Send a GET request to the user API with the sender_id and headers, convert the response to JSON and store the sender, and store the sender's username in the message
            response = requests.get(f'https://vintekapi.pythonanywhere.com/user/{message["sender_id"]}/', headers=headers)
            sender = response.json() if response.status_code == 200 else {}
            message['sender_name'] = sender.get('username')

            # Send a GET request to the products API with the product_id and headers, convert the response to JSON and store the product, and store the product's name in the message
            response = requests.get(f'https://vintekapi.pythonanywhere.com/api/products/{message["product_id"]}/', headers=headers)
            product = response.json() if response.status_code == 200 else {}
            message['product_name'] = product.get('name')

        # Add the messages to the context
        context['messages'] = messages

        # Return the context
        return context
    

# This is a Django class-based view for creating a reply to a message.
class ReplyCreateView(FormView):
    # The form to be used in this view is ReplyForm.
    form_class = ReplyForm
    # The template to be used in this view is 'user_messages.html'.
    template_name = 'user_messages.html'

    # This method is called when the form is valid.
    def form_valid(self, form):
        # Get the user_id from the session.
        user_id = self.request.session.get('user_id')
        # Get the token from the session.
        token = self.request.session.get('token')
        # Create headers for the request. If token exists, add it to the headers.
        headers = {'Authorization': f'Token {token}'} if token else {}
        # Get the original_message_id from the form data.
        original_message_id = form.cleaned_data.get('original_message_id')
        # Get the recipient from the form data.
        recipient = form.cleaned_data.get('recipient')
        # Get the product from the form data.
        product = form.cleaned_data.get('product')

        # Create the message data to be sent in the request.
        message_data = {
            'sender': user_id,
            'recipient': recipient,
            'product': int(product),
            'message': form.cleaned_data.get('message'),
            'reply_to': original_message_id,
        }
        
        # Send a POST request to the server to create a reply.
        response = requests.post('https://vintekapi.pythonanywhere.com/messages/reply_create/', data=message_data, headers=headers)
        
        # If the response status code is 201, the reply was created successfully.
        if response.status_code == 201:
            messages.success(self.request, 'Reply sent successfully')
        else:
            # If the status code is not 201, there was an error creating the reply.
            messages.error(self.request, 'Failed to send reply')
        # Redirect to the 'user_messages' view.
        return redirect('user_messages')

    # This method is called when the form is invalid.
    def form_invalid(self, form):
        # Call the parent class's form_invalid method.
        return super().form_invalid(form)


# This is a Django class-based view for deleting a conversation.
class DeleteConversationView(View):
    # This method is called when a POST request is made to this view.
    def post(self, request, product_id):
        # Get the token from the session.
        token = request.session.get('token')
        # Create headers for the request. If token exists, add it to the headers.
        headers = {'Authorization': f'Token {token}'} if token else {}
        # Send a DELETE request to the server to delete the conversation.
        response = requests.delete(f'https://vintekapi.pythonanywhere.com/messages/delete_conversation/{product_id}/', headers=headers)
        # If the response status code is 200, the conversation was deleted successfully.
        if response.status_code == 200:
            messages.success(request, 'Conversation deleted successfully')
        else:
            # If the status code is not 200, there was an error deleting the conversation.
            messages.error(request, 'Failed to delete conversation')
        # Redirect to the 'user_messages' view.
        return redirect('user_messages')
    
# -----------------About-------------------------------------------------------------------------------------------------------------------------------

class About(TemplateView):
    # Define the template name for this view
    template_name = 'about.html'