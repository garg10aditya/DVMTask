from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
import csv
import datetime
from django.http import HttpResponse
from django.views import View
from .models import Category, Product, Order, OrderItem, Review, Wishlist
from .cart import Cart
from .forms import OrderForm, SignUpForm
from mailjet_rest import Client
from django.conf import settings



@login_required
def product_detail(request, category_slug, slug):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')

    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE)

    if request.method == 'POST':
        content = request.POST.get('content')
        rating = int(request.POST.get('rating'))

        has_ordered = Order.objects.filter(created_by=request.user, items__product=product).exists()
        if has_ordered:
            # User has ordered the product before, allow writing the review
            Review.objects.create(user=request.user, product=product, content=content, rating=rating)
            return redirect('product_detail', category_slug=category_slug, slug=slug)
        else:
            messages.error(request, "You can only write a review for products you have ordered.")

    reviews = Review.objects.filter(product=product)

    # Wishlist functionality
    # is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart': cart,
        'reviews': reviews,
        # 'is_in_wishlist': is_in_wishlist,
    })


# @login_required
# def add_to_wishlist(request, product_id):
#     product = get_object_or_404(Product, id=product_id, status=Product.ACTIVE)
#
#     wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
#
#     if created:
#         messages.success(request, f"{product.title} added to wishlist.")
#     else:
#         messages.info(request, f"{product.title} is already in your wishlist.")
#
#     return redirect('product_detail', category_slug=product.category.slug, slug=product.slug)


# @login_required
# def remove_from_wishlist(request, product_id):
#     product = get_object_or_404(Product, id=product_id, status=Product.ACTIVE)
#
#     Wishlist.objects.filter(user=request.user, product=product).delete()
#     messages.success(request, f"{product.title} removed from wishlist.")
#
#     return redirect('product_detail', category_slug=product.category.slug, slug=product.slug)
#

# @login_required
# def wishlist(request):
#     wishlist_items = Wishlist.objects.filter(user=request.user)
#     return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


def add_to_cart(request, product_id):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')

    product = get_object_or_404(Product, id=product_id, status=Product.ACTIVE)

    if product.avail_qty == 0:
        messages.error(request, f"{product.title} is out of stock. It cannot be added to the cart.")
        return redirect('frontpage')

    quantity = int(request.GET.get('quantity', 1))
    cart = Cart(request)
    added = cart.add(product_id, quantity)

    if added:
        # Item added successfully
        return redirect('cart_view')

    return redirect('frontpage')


def success(request):
    return render(request, 'store/success.html')


def change_quantity(request, product_id):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')
    action = request.GET.get('action', '')
    if action:
        quantity = 1
        if action == 'decrease':
            quantity = -1

        cart = Cart(request)
        cart.add(product_id, quantity, True)

        if quantity > 0:
            messages.success(request, "Product quantity increased successfully.")
        elif quantity < 0:
            messages.success(request, "Product quantity decreased successfully.")

    return redirect('cart_view')


def remove_from_cart(request, product_id):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')
    cart = Cart(request)
    cart.remove(str(product_id))

    messages.success(request, "Product removed from the cart successfully.")
    return redirect('frontpage')


def cart_view(request):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')
    cart = Cart(request)
    return render(request, 'store/cart_view.html', {'cart': cart})


from django.shortcuts import get_object_or_404


@login_required
def checkout(request):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')

    cart = Cart(request)
    if cart.get_total_cost() == 0:
        return redirect('cart_view')

    total_price = 0

    # Calculate the total price of the items in the cart
    for item in cart:
        product = item['product']
        total_price += product.price * int(item['quantity'])

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            user_profile = request.user.userprofile

            if user_profile.balance >= total_price:
                order = form.save(commit=False)
                order.created_by = request.user
                order.is_paid = True
                order.total_cost = total_price

                # Check if the ordered quantity exceeds the available quantity
                for item in cart:
                    product = item['product']
                    quantity = int(item['quantity'])
                    if quantity > product.avail_qty:
                        messages.error(request, f"Insufficient quantity available for {product.title}. Maximum available quantity: {product.avail_qty}.")
                        return redirect('cart_view')

                order.save()

                for item in cart:
                    product = item['product']
                    quantity = int(item['quantity'])
                    price = product.price * quantity
                    order_item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)

                    # Decrease the available quantity of the product
                    product.avail_qty -= quantity
                    product.save()

                    # Increase the balance of the vendor
                    vendor = product.user.userprofile
                    vendor.balance += price
                    vendor.save()

                # Deduct the total cost from the user's balance
                user_profile.balance -= total_price
                user_profile.save()

                cart.clear()

                # Send order notification email
                send_order_notification_email(order, vendor.email)

                return redirect('success', order_id=order.id)  # Pass the order ID as a parameter
            else:
                messages.error(request, "Insufficient account balance to complete the order.")
    else:
        form = OrderForm()

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'form': form,
        'total_price': total_price,
    })


def success(request, order_id):
    order = get_object_or_404(Order, id=order_id, created_by=request.user)
    return render(request, 'store/success.html', {'order': order})


def search(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(status=Product.ACTIVE).filter(
        Q(title__icontains=query) | Q(description__icontains=query))

    return render(request, 'store/search.html', {
        'query': query,
        'products': products,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(status=Product.ACTIVE)

    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products
    })


def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart_view')  # Replace 'cart' with the appropriate URL name for your cart page


def submit_review(request):
    if request.method == 'POST':
        # Process the submitted review data
        # Create a new instance of the Review model

        # Example: Save a new review
        review = Review(content=request.POST['content'], rating=request.POST['rating'])
        review.save()

        # Perform any other necessary actions

        return redirect('review_success')  # Redirect to a success page after submitting the review

    return render(request, 'frontpage.html')

class SalesReportView(View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Product', 'Price', 'Quantity', 'Total Cost', 'Date'])

        orders = Order.objects.filter(created_by=request.user)

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)

            for order_item in order_items:
                writer.writerow([
                    order.id,
                    order_item.product.title,
                    order_item.price,
                    order_item.quantity,
                    order.total_cost,
                    order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])

        return response
def send_order_notification_email(order, vendor_email):
    mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')

    data = {
        'Messages': [
            {
                'From': {
                    'Email': settings.MAILJET_SENDER_EMAIL,
                    'Name': 'BITShop Notification'
                },
                'To': [
                    {
                        'Email': vendor_email,
                        'Name': 'Vendor'
                    }
                ],
                'Subject': 'New Order Notification',
                'TextPart': 'You have received a new order.',
                'HTMLPart': '<p>You have received a new order.</p>'
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code == 200:
        print('Order notification email sent successfully.')
    else:
        print('Failed to send order notification email. Error:', result.json())
