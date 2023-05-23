from django.contrib.auth import get_user_model
from allauth.account.views import LoginView

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from decimal import Decimal
from .models import Userprofile
from django import forms
from store.models import Wishlist


from store.forms import ProductForm, SignUpForm
from store.models import Product, Order, OrderItem


def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products = user.products.filter(status=Product.ACTIVE)

    return render(request, 'userprofile/vendor_detail.html', {
        'user': user,
        'products': products,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Userprofile


class GoogleAuthLoginView(LoginView):
    template_name = 'accounts/login.html'
@login_required
def my_store(request):
    if request.user.userprofile.is_vendor:
        # User is a vendor, allow access to my-store.html
        products = request.user.products.exclude(status=Product.DELETED)
        order_items = OrderItem.objects.filter(product__user=request.user)
        return render(request, 'userprofile/my_store.html', {
            'products': products,
            'order_items': order_items,
        })
    else:
        # User is not a vendor, redirect to frontpage
        return redirect('frontpage')


@login_required
def add_money(request):
    if request.user.userprofile.is_vendor:
        return redirect('my_store')

    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        account = Userprofile.objects.get(user=request.user)
        account.balance += amount
        account.save()
        return redirect('myaccount')

    return render(request, 'userprofile/add_money.html')



@login_required
def my_store_order_detail(request, pk):
    if not request.user.userprofile.is_vendor:
        return redirect('frontpage')

    order = get_object_or_404(Order, pk=pk)

    # Deduct the total cost of the order from the user's balance
    user_profile = Userprofile.objects.get(user=request.user)
    # user_profile.balance -= order.total_cost
    user_profile.save()

    return render(request, 'userprofile/my_store_order_detail.html', {
        'order': order
    })


@login_required
def add_product(request):
    if not request.user.userprofile.is_vendor:
        return redirect('my_store')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            title = request.POST.get('title')

            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()

            messages.success(request, 'The product was added!')

            return redirect('my_store')
    else:
        form = ProductForm()

    return render(request, 'userprofile/product_form.html', {
        'title': 'Add product',
        'form': form
    })

@login_required
def edit_product(request, pk):
    if not request.user.userprofile.is_vendor:
        return redirect('frontpage')

    product = Product.objects.filter(user=request.user).get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()

            messages.success(request, 'The changes was saved!')

            return redirect('my_store')
    else:
        form = ProductForm(instance=product)

    return render(request, 'userprofile/product_form.html', {
        'title': 'Edit product',
        'product': product,
        'form': form
    })


@login_required
def delete_product(request, pk):
    if not request.user.userprofile.is_vendor:
        return redirect('frontpage')

    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()

    messages.success(request, 'The product was deleted!')

    return redirect('my_store')


@login_required
def myaccount(request):
    user = request.user
    userprofile = user.userprofile
    return render(request, 'userprofile/myaccount.html', {
        'user': user,
        'userprofile': userprofile,
    })




User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            userprofile = Userprofile.objects.create(user=user)
            userprofile.is_vendor = form.cleaned_data.get('is_vendor')
            userprofile.save()

            login(request, user)
            return redirect('frontpage')
    else:
        form = SignUpForm()

    return render(request, 'userprofile/signup.html', {'form': form})

class EditProfileForm(SignUpForm):
    username = forms.CharField(disabled=True, required=False)
    email = forms.CharField(disabled=True, required=False)
    is_vendor = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_vendor')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

            messages.success(request, 'Your profile has been updated!')
            return redirect('myaccount')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'userprofile/edit_profile.html', {'form': form})

@login_required
def past_orders(request):
    user = request.user
    past_orders = Order.objects.filter(created_by=user)

    return render(request, 'store/past_orders.html', {'past_orders': past_orders})

@login_required
def user_order_detail(request, pk):
    if request.user.userprofile.is_vendor:
        return redirect('frontpage')

    order = get_object_or_404(Order, pk=pk)

    # Deduct the total cost of the order from the user's balance
    user_profile = Userprofile.objects.get(user=request.user)
    # user_profile.balance -= order.total_cost
    user_profile.save()

    return render(request, 'store/user_order_details.html', {
        'order': order
    })

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, status=Product.ACTIVE)

    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f"{product.title} added to wishlist.")
    elif wishlist:
        messages.info(request, f"{product.title} is already in your wishlist.")
    else:
        messages.error(request, "Failed to add the product to the wishlist.")

    return redirect('product_detail', category_slug=product.category.slug, slug=product.slug)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, status=Product.ACTIVE)

    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.title} removed from wishlist.")

    return redirect('product_detail', category_slug=product.category.slug, slug=product.slug)


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'userprofile/wishlist.html', {'wishlist_items': wishlist_items})

