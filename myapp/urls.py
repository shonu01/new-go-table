from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, RestaurantViewSet, TableViewSet, BookingViewSet, RegisterView,
    admin_dashboard, restaurant_list, restaurant_create, restaurant_edit, restaurant_delete,
    table_list, table_create, table_edit, table_delete, booking_list, booking_edit, booking_delete,
    dashboard, user_dashboard
)
from .frontend_views import (
    home, login_view, logout_view, register, profile,
    restaurant_list as frontend_restaurant_list,
    restaurant_detail, booking_list as frontend_booking_list,
    booking_detail, cancel_booking, password_reset_request,
    password_reset_done, password_reset_confirm, password_reset_complete
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'restaurants', RestaurantViewSet)
router.register(r'tables', TableViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # API URLs
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Frontend URLs
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    
    # Restaurant URLs
    path('restaurants/', frontend_restaurant_list, name='restaurant_list'),
    path('restaurants/<int:pk>/', restaurant_detail, name='restaurant_detail'),
    
    # Booking URLs
    path('bookings/', frontend_booking_list, name='booking_list'),
    path('bookings/<int:pk>/', booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/cancel/', cancel_booking, name='cancel_booking'),
    
    # Password Reset URLs
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),
    
    # Dashboard URLs
    path('dashboard/', dashboard, name='dashboard'),
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Admin URLs
    path('admin/restaurants/', restaurant_list, name='admin_restaurant_list'),
    path('admin/restaurants/create/', restaurant_create, name='restaurant_create'),
    path('admin/restaurants/<int:pk>/edit/', restaurant_edit, name='restaurant_edit'),
    path('admin/restaurants/<int:pk>/delete/', restaurant_delete, name='restaurant_delete'),
    path('admin/tables/', table_list, name='table_list'),
    path('admin/tables/create/', table_create, name='table_create'),
    path('admin/tables/<int:pk>/edit/', table_edit, name='table_edit'),
    path('admin/tables/<int:pk>/delete/', table_delete, name='table_delete'),
    path('admin/bookings/', booking_list, name='admin_booking_list'),
    path('admin/bookings/<int:pk>/edit/', booking_edit, name='booking_edit'),
    path('admin/bookings/<int:pk>/delete/', booking_delete, name='booking_delete'),
] 