from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import Restaurant, Booking, CustomUser
from .forms import UserRegistrationForm, LoginForm, ProfileForm

def home(request):
    """Home page view with featured restaurants."""
    featured_restaurants = Restaurant.objects.filter(
        is_active=True
    ).order_by('-created_at')[:6]
    return render(request, 'myapp/home.html', {
        'featured_restaurants': featured_restaurants
    })

def restaurant_list(request):
    """List all restaurants with search and filtering."""
    restaurants = Restaurant.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        restaurants = restaurants.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(cuisine_type__icontains=search_query)
        )
    
    # Filter by cuisine type
    cuisine = request.GET.get('cuisine')
    if cuisine:
        restaurants = restaurants.filter(cuisine_type=cuisine)
    
    # Filter by price range
    price_range = request.GET.get('price')
    if price_range:
        restaurants = restaurants.filter(price_range=price_range)
    
    # Filter by availability
    date = request.GET.get('date')
    time = request.GET.get('time')
    if date and time:
        # Get restaurants with available tables
        restaurants = restaurants.filter(
            tables__status='available'
        ).exclude(
            tables__bookings__date=date,
            tables__bookings__time=time,
            tables__bookings__status__in=['pending', 'confirmed']
        ).distinct()
    
    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'name':
        restaurants = restaurants.order_by('name')
    elif sort_by == '-rating':
        restaurants = sorted(restaurants, key=lambda x: x.get_rating(), reverse=True)
    elif sort_by == '-created_at':
        restaurants = restaurants.order_by('-created_at')
    elif sort_by == 'price':
        restaurants = restaurants.order_by('price_range')
    
    # Get unique cuisine types for filter
    cuisine_types = Restaurant.objects.filter(
        is_active=True
    ).values_list('cuisine_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(restaurants, 9)
    page_number = request.GET.get('page')
    restaurants = paginator.get_page(page_number)
    
    return render(request, 'myapp/restaurant_list.html', {
        'restaurants': restaurants,
        'cuisine_types': cuisine_types,
        'search_query': search_query,
        'selected_cuisine': cuisine,
        'selected_price': price_range,
        'selected_date': date,
        'selected_time': time,
        'sort_by': sort_by
    })

def restaurant_detail(request, pk):
    """Show restaurant details and booking form."""
    restaurant = get_object_or_404(Restaurant, pk=pk, is_active=True)
    
    # Generate time slots for the booking form
    time_slots = []
    for hour in range(11, 22):  # 11 AM to 10 PM
        time_slots.append(f"{hour:02d}:00")
    
    # Get today's date for the date input min attribute
    today = timezone.now().date()
    
    # Get number of bookings for today
    bookings_today = Booking.objects.filter(
        table__restaurant=restaurant,
        date=today
    ).count()
    
    # Get available tables for today
    available_tables = restaurant.get_available_tables(today, timezone.now().time())
    
    return render(request, 'myapp/restaurant_detail.html', {
        'restaurant': restaurant,
        'time_slots': time_slots,
        'today': today,
        'bookings_today': bookings_today,
        'available_tables': available_tables
    })

@login_required
def booking_list(request):
    """Show user's booking history."""
    bookings = Booking.objects.filter(user=request.user)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by date
    date = request.GET.get('date')
    if date:
        bookings = bookings.filter(date=date)
    
    # Sort by date and time
    bookings = bookings.order_by('-date', '-time')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    return render(request, 'myapp/booking_list.html', {
        'bookings': bookings
    })

@login_required
def booking_detail(request, pk):
    """Show detailed information about a specific booking."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'myapp/booking_detail.html', {
        'booking': booking
    })

@login_required
def cancel_booking(request, pk):
    """Cancel a booking."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    
    return redirect('booking_detail', pk=pk)

def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'myapp/register.html', {
        'form': form
    })

def login_view(request):
    """Custom login view with role-based redirection."""
    if request.user.is_authenticated:
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect based on user role
                if user.is_superuser or user.is_staff:
                    return redirect('admin_dashboard')
                elif user.is_restaurant_admin:
                    return redirect('restaurant_admin_dashboard')
                else:
                    return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'myapp/login.html', {'form': form})

@login_required
def user_dashboard(request):
    """User dashboard view."""
    if request.user.is_superuser or request.user.is_staff or request.user.is_restaurant_admin:
        return redirect('admin_dashboard')
        
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'myapp/user_dashboard.html', {
        'bookings': bookings
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_dashboard(request):
    """Admin dashboard view."""
    restaurants = Restaurant.objects.all()
    bookings = Booking.objects.all()
    users = CustomUser.objects.all()
    
    return render(request, 'myapp/admin_dashboard.html', {
        'restaurants': restaurants,
        'bookings': bookings,
        'users': users
    })

@login_required
@user_passes_test(lambda u: u.is_restaurant_admin)
def restaurant_admin_dashboard(request):
    """Restaurant admin dashboard view."""
    restaurants = Restaurant.objects.filter(admin=request.user)
    bookings = Booking.objects.filter(table__restaurant__admin=request.user)
    
    return render(request, 'myapp/restaurant_admin_dashboard.html', {
        'restaurants': restaurants,
        'bookings': bookings
    })

def logout_view(request):
    """Handle user logout and redirect to login page."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def password_reset_request(request):
    """Handle password reset request."""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset link
                reset_url = request.build_absolute_uri(
                    f'/reset/{uid}/{token}/'
                )
                
                # Send email
                subject = 'Password Reset Requested'
                message = f'''
                Hello {user.username},
                
                You recently requested to reset your password for your GoTable account. Click the link below to reset it:
                
                {reset_url}
                
                If you did not request a password reset, please ignore this email or contact support if you have concerns.
                
                This password reset link will expire in 24 hours.
                
                Best regards,
                The GoTable Team
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset email has been sent.')
                return redirect('password_reset_done')
            else:
                messages.error(request, 'No user found with this email address.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'myapp/password_reset.html', {'form': form})

def password_reset_done(request):
    """Show password reset email sent confirmation."""
    return render(request, 'myapp/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password1')
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
    else:
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('password_reset')
    
    return render(request, 'myapp/password_reset_confirm.html')

def password_reset_complete(request):
    """Show password reset complete confirmation."""
    return render(request, 'myapp/password_reset_complete.html')

@login_required
def profile(request):
    """Allow users to update their profile information."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_dashboard')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'myapp/profile.html', {'form': form}) 