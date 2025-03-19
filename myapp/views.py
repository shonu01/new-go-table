from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate, login
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from .models import Restaurant, Table, Booking
from .serializers import (
    UserSerializer, RestaurantSerializer, TableSerializer, BookingSerializer
)
from .frontend_views import (
    home, restaurant_list, restaurant_detail,
    booking_list, booking_detail, cancel_booking,
    register
)
from .forms import RestaurantForm, TableForm, BookingForm, LoginForm

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return super().get_permissions()

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Restaurant.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Table.objects.all()
        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_restaurant_admin:
            return Booking.objects.filter(table__restaurant__admin=user)
        return Booking.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if request.user.is_restaurant_admin and booking.table.restaurant.admin == request.user:
            booking.status = 'confirmed'
            booking.save()
            return Response({'status': 'booking confirmed'})
        return Response(
            {'error': 'Not authorized to confirm this booking'},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if request.user == booking.user or (request.user.is_restaurant_admin and booking.table.restaurant.admin == request.user):
            booking.status = 'cancelled'
            booking.save()
            return Response({'status': 'booking cancelled'})
        return Response(
            {'error': 'Not authorized to cancel this booking'},
            status=status.HTTP_403_FORBIDDEN
        )

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard(request):
    """Admin dashboard view."""
    total_restaurants = Restaurant.objects.count()
    total_tables = Table.objects.count()
    total_bookings = Booking.objects.count()
    recent_bookings = Booking.objects.select_related('user', 'table__restaurant').order_by('-created_at')[:10]
    
    context = {
        'total_restaurants': total_restaurants,
        'total_tables': total_tables,
        'total_bookings': total_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'myapp/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_admin)
def restaurant_list(request):
    """List all restaurants for admin management."""
    restaurants = Restaurant.objects.all().order_by('name')
    return render(request, 'myapp/restaurant_list.html', {'restaurants': restaurants})

@login_required
@user_passes_test(lambda u: u.is_admin)
def restaurant_create(request):
    """Create a new restaurant."""
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant created successfully.')
            return redirect('admin_restaurant_list')
    else:
        form = RestaurantForm()
    return render(request, 'myapp/restaurant_form.html', {'form': form, 'title': 'Add Restaurant'})

@login_required
@user_passes_test(lambda u: u.is_admin)
def restaurant_edit(request, pk):
    """Edit an existing restaurant."""
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant updated successfully.')
            return redirect('admin_restaurant_list')
    else:
        form = RestaurantForm(instance=restaurant)
    return render(request, 'myapp/restaurant_form.html', {'form': form, 'title': 'Edit Restaurant'})

@login_required
@user_passes_test(lambda u: u.is_admin)
def restaurant_delete(request, pk):
    """Delete a restaurant."""
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully.')
        return redirect('admin_restaurant_list')
    return render(request, 'myapp/restaurant_confirm_delete.html', {'restaurant': restaurant})

@login_required
@user_passes_test(is_admin)
def table_list(request):
    tables = Table.objects.select_related('restaurant').all().order_by('restaurant__name', 'table_number')
    return render(request, 'myapp/table_list.html', {'tables': tables})

@login_required
@user_passes_test(is_admin)
def table_create(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table created successfully.')
            return redirect('table_list')
    else:
        form = TableForm()
    return render(request, 'myapp/table_form.html', {'form': form, 'title': 'Add Table'})

@login_required
@user_passes_test(is_admin)
def table_edit(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table updated successfully.')
            return redirect('table_list')
    else:
        form = TableForm(instance=table)
    return render(request, 'myapp/table_form.html', {'form': form, 'title': 'Edit Table'})

@login_required
@user_passes_test(is_admin)
def table_delete(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        table.delete()
        messages.success(request, 'Table deleted successfully.')
        return redirect('table_list')
    return render(request, 'myapp/table_confirm_delete.html', {'table': table})

@login_required
@user_passes_test(is_admin)
def booking_list(request):
    bookings = Booking.objects.select_related('user', 'table__restaurant').all().order_by('-created_at')
    return render(request, 'myapp/booking_list.html', {'bookings': bookings})

@login_required
@user_passes_test(is_admin)
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully.')
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'myapp/booking_form.html', {'form': form, 'title': 'Edit Booking'})

@login_required
@user_passes_test(is_admin)
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully.')
        return redirect('booking_list')
    return render(request, 'myapp/booking_confirm_delete.html', {'booking': booking})

@login_required
def dashboard(request):
    """Redirect users to their appropriate dashboard based on their role."""
    if request.user.is_admin:
        return redirect('admin_dashboard')
    elif request.user.is_customer:
        return redirect('user_dashboard')
    else:
        return redirect('home')

@login_required
def user_dashboard(request):
    """Display the user dashboard with bookings and restaurant recommendations."""
    if not request.user.is_customer:
        messages.error(request, 'Access denied. This page is for customers only.')
        return redirect('home')
    
    # Get user's bookings
    today = timezone.now().date()
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')
    
    past_bookings = Booking.objects.filter(
        user=request.user,
        date__lt=today
    ).order_by('-date', '-time')[:10]
    
    # Get recommended restaurants
    recommended_restaurants = Restaurant.objects.filter(
        is_active=True
    ).exclude(
        tables__bookings__user=request.user
    ).distinct()[:6]
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'recommended_restaurants': recommended_restaurants,
    }
    return render(request, 'myapp/user_dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to role-based dashboard
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'myapp/login.html', {'form': form})
