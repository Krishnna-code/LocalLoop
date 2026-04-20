
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, UserProfile, Booking
from .forms import RegisterForm, ProductForm

def home(request):
    try:
        products = Product.objects.filter(is_available=True).order_by('-created_at')[:6]
    except:
        products = []
    return render(request, 'home.html', {'products': products})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                aadhaar_number=form.cleaned_data['aadhaar_number'],
                address=form.cleaned_data['address']
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, 'Listing created successfully!')
            return redirect('my_listings')
    else:
        form = ProductForm()
    return render(request, 'create_listing.html', {'form': form})

def product_list(request):
    category = request.GET.get('category', '')
    if category:
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
        'today': date.today().isoformat()  # ADD this line
    }
    return render(request, 'product_detail.html', context)

@login_required
def my_listings(request):
    products = Product.objects.filter(owner=request.user)
    return render(request, 'my_listings.html', {'products': products})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized access')
        return redirect('home')
    
    total_users = UserProfile.objects.count()
    total_products = Product.objects.count()
    total_bookings = Booking.objects.count()
    
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_bookings': total_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin_dashboard.html', context)



    # ADD these imports at the top if not already there
from django.http import JsonResponse
from datetime import datetime, timedelta, date

# ADD these NEW functions at the bottom of views.py

@login_required
def create_booking(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        
        if product.owner == request.user:
            messages.error(request, 'You cannot book your own product!')
            return redirect('product_detail', pk=product_id)
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        duration = (end - start).days
        
        if duration < 1:
            messages.error(request, 'End date must be after start date!')
            return redirect('product_detail', pk=product_id)
        
        if duration > product.max_lending_days:
            messages.error(request, f'Maximum lending period is {product.max_lending_days} days!')
            return redirect('product_detail', pk=product_id)
        
        total_amount = duration * product.price_per_day
        
        booking = Booking.objects.create(
            product=product,
            borrower=request.user,
            start_date=start,
            end_date=end,
            total_amount=total_amount,
            status='pending'
        )
        
        messages.success(request, f'Booking request sent! Total: ₹{total_amount + product.security_deposit}')
        return redirect('my_bookings')
    
    return redirect('product_detail', pk=product_id)

@login_required
def my_bookings(request):
    my_requests = Booking.objects.filter(borrower=request.user).order_by('-created_at')
    received_requests = Booking.objects.filter(product__owner=request.user).order_by('-created_at')
    
    context = {
        'my_requests': my_requests,
        'received_requests': received_requests,
    }
    return render(request, 'my_bookings.html', context)

@login_required
def booking_action(request, booking_id, action):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if booking.product.owner != request.user:
        messages.error(request, 'Unauthorized action!')
        return redirect('my_bookings')
    
    if action == 'accept':
        booking.status = 'accepted'
        booking.product.is_available = False
        booking.product.save()
        messages.success(request, 'Booking accepted!')
    elif action == 'reject':
        booking.status = 'rejected'
        messages.success(request, 'Booking rejected!')
    
    booking.save()
    return redirect('my_bookings')

@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if booking.borrower != request.user and booking.product.owner != request.user:
        messages.error(request, 'Unauthorized action!')
        return redirect('my_bookings')
    
    booking.status = 'completed'
    booking.product.is_available = True
    booking.product.save()
    booking.save()
    
    messages.success(request, 'Booking completed!')
    return redirect('my_bookings')