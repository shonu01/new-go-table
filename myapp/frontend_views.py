from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Restaurant, Booking
from .forms import UserRegistrationForm

def home(request):
    """Home page view with featured restaurants."""
    featured_restaurants = Restaurant.objects.filter(is_active=True)[:6]
    return render(request, 'myapp/home.html', {
        'featured_restaurants': featured_restaurants
    })

def restaurant_list(request):
    """List all restaurants with search and filtering."""
    restaurants = Restaurant.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        restaurants = restaurants.filter(name__icontains=search_query) | \
                     restaurants.filter(address__icontains=search_query)
    
    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'name':
        restaurants = restaurants.order_by('name')
    elif sort_by == '-created_at':
        restaurants = restaurants.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(restaurants, 9)
    page_number = request.GET.get('page')
    restaurants = paginator.get_page(page_number)
    
    return render(request, 'myapp/restaurant_list.html', {
        'restaurants': restaurants
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
    
    return render(request, 'myapp/restaurant_detail.html', {
        'restaurant': restaurant,
        'time_slots': time_slots,
        'today': today,
        'bookings_today': bookings_today
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