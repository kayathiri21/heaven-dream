from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q

from django.utils import timezone
import uuid
import razorpay
from django.http import JsonResponse


from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Product, Wishlist, Cart, Order
from django.template.loader import render_to_string
from django.conf import settings
import stripe
razorpay_client = razorpay.Client(auth=("rzp_test_zQlH0LBPdTUM8A", "iN6L05wEXMFfgboXs66EemtT"))

def index(request):
    wishlist_count = 0
    cart_count=0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    
    return render(request, './app/index.html', {'wishlist_count': wishlist_count,'cart_count': cart_count})

def category(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    categories = Category.objects.all()
    return render(request, './app/catagories.html', {'categories': categories,'wishlist_count': wishlist_count})
def product_list(request, category_id):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    
    return render(request, './app/product.html', {'category': category, 'products': products ,'wishlist_count': wishlist_count})
def featureproduct(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    products = Product.objects.all()
    return render(request, './app/featureproduct.html', {'products': products,'wishlist_count': wishlist_count})
def product_detail(request, product_id):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    product = get_object_or_404(Product, pk=product_id)
     # Find similar products based on category
    similar_products = Product.objects.filter(Q(category=product.category) & ~Q(id=product.id))[:3]  # Adjust the number of similar products to display

    return render(request, './app/product_detail.html', {'product': product, 'similar_products': similar_products,'wishlist_count': wishlist_count})



def signup_view(request):

    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        password2=request.POST['password2']
        if password==password2:
            if User.objects.filter(username=username).exists():
               messages.error(request,'username already exists')
               return redirect('app:login')  
            else:       
                user=User.objects.create_user(username=username,password=password)
                login(request,user)
                messages.success(request,'You are signup successful')
                return redirect('app:signup')
        else:
            messages.error(request,'passwords do not match')
            return redirect('app:signup')
    return render(request,'./registration/signup.html')

def login_view(request):
   
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"You are logged in")
            return redirect('app:login')
        else:
             messages.error(request,"invalid requst")
             return redirect('app:login')
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'./registration/login.html',{'wishlist_count': wishlist_count})

def logout_view(request):
   logout(request)
  
   return render(request,'./app/index.html')# Redirect to the home page after logout

@login_required
def profile_view(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request, './registration/profile.html',{'wishlist_count': wishlist_count})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        # If the wishlist item already exists, delete it (to remove from the wishlist)
        wishlist_item.delete()
        messages.success(request, "Product removed from wishlist successfully.")
    else:
        messages.success(request, "Product added to wishlist successfully.")
    return redirect('app:product_detail', product_id=product_id)



@login_required
def view_wishlist(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, './app/wishlist.html', {'wishlist_items': wishlist_items,'wishlist_count': wishlist_count})


@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(product=product, 
                                                       user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('app:cart')
@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = 0
    
    # Calculate total amount and subtotal for each item
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total_amount += item.subtotal
    
    return render(request, './app/cart.html', {'cart': cart_items, 'total_amount': total_amount})


    



def remove_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id)
    cart_item.delete()
    return redirect('app:cart')
# Function to generate an invoice




# Function to handle payment success
def handle_payment_success(request, order):
    # Generate invoice number
    invoice_number = generate_invoice_number(order)
    
    # Get the current date
    invoice_date = timezone.now().date()

    # Generate invoice
    invoice_html = generate_invoice(order, invoice_number, invoice_date)
    
    # Send invoice via email
    send_invoice_email(order.email, invoice_html, invoice_number)

    # Display success message
    messages.success(request, "Payment successful. Order placed.")

    return redirect('app:index')

# Function to handle payment failure
def handle_payment_failure(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect('app:checkout')
def success(request):
    return render(request, './app/success.html')
def cancel(request):
    return render(request, './app/cancel.html')


     
def generate_invoice(order, invoice_number,invoice_date):
    # Get the current date
    invoice_date = timezone.now().date()
    
    # Create a dictionary or data structure containing order, product details, and invoice date
    context = {
        'order': order,
       
        'invoice_number': invoice_number,
        'invoice_date': invoice_date,  # Include the invoice date in the context
        # Add other necessary details such as total amount, etc.
    }
    # Render the invoice template to HTML string
    invoice_html = render_to_string('./app/invoice.html', context)
    return invoice_html

# Function to send an email with the invoice attached
def send_invoice_email(email, invoice_html, invoice_number, invoice_date):
    subject = f'Your Invoice {invoice_number} from MyStore'  # Include invoice number in the subject
    message = f'Please find attached the invoice {invoice_number} for your recent purchase made on {invoice_date}.'  # Include invoice number and date in the message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list, html_message=invoice_html)         

def generate_invoice_number(order):
    # Generate a UUID for uniqueness
    unique_id = str(uuid.uuid4()).split('-')[-1]
    # Combine with order details to create the invoice number
    invoice_number = f"{order.id}-{unique_id}"
    return invoice_number
def checkout(request):
    cart_items = Cart.objects.all()  # Adjust this query based on your actual logic
    total_amount = sum(item.product.price for item in cart_items)
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        payment_method = request.POST.get('payment_method')

        order = Order.objects.create(name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, payment_method=payment_method)

        if payment_method == 'COD':
                 # Generate invoice number
            invoice_number = generate_invoice_number(order)
    
            # Get the current date
            invoice_date = timezone.now().date()

            # Create invoice HTML
            invoice_html = generate_invoice(order, invoice_number, invoice_date)
    
            # Send email with invoice and invoice number
            send_invoice_email(email, invoice_html, invoice_number, invoice_date)
    
            messages.success(request, "Order placed successfully. You will receive an invoice via email.")
            return redirect('app:index')
        elif payment_method =='card':
            try:
                
                # Create Razorpay order
                 new_order_response = razorpay_client.order.create({"amount":int(total_amount)* 100," currency ": 'INR',"payment_capture": "1"
                        })

                 # Verify Razorpay payment signature
                 payment_id = request.POST.get('razorpay_payment_id', '')
                 razorpay_order_id = request.POST.get('razorpay_order_id', '')
                 signature = request.POST.get('razorpay_signature', '')

                 params_dict = {
                  'razorpay_order_id': razorpay_order_id,
                  'razorpay_payment_id': payment_id,
                  'razorpay_signature': signature
                }

                 result = razorpay_client.utility.verify_payment_signature(params_dict)

                 if result is not None:
                 # Payment signature verification successful
                  amount = total_amount * 100  # Convert amount to paise
                  razorpay_client.payment.capture(payment_id, amount)
                  return render(request, 'paymentsuccess.html')
           
                
                # Generating invoice with number and date
                 invoice_number = generate_invoice_number(order)
                 invoice_date = timezone.now().date()
                 invoice_html = generate_invoice(order, invoice_number, invoice_date)

                 # Sending the modified invoice via email
                 send_invoice_email(email, invoice_html, invoice_number, invoice_date)
                
                 order_id = new_order_response['id']

                 # Redirect or display success message with order ID
                 messages.success(request, f"Payment successful. Your order ID is {order_id}.")
                 return redirect('app:index')
            except Exception as e:
               messages.error(request, f"Payment failed. Please try again: {e}")
               return redirect('app:checkout')

    return render(request, 'app/checkout.html', { 'total_amount': total_amount, 'cart': cart_items})
