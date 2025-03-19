"""
URL configuration for gotable project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from myapp import views, frontend_views

urlpatterns = [
    path('', frontend_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    # Frontend URLs
    path('restaurants/', frontend_views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:pk>/', frontend_views.restaurant_detail, name='restaurant_detail'),
    path('bookings/', frontend_views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/', frontend_views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/cancel/', frontend_views.cancel_booking, name='cancel_booking'),
    # Authentication URLs
    path('login/', frontend_views.login_view, name='login'),
    path('logout/', frontend_views.logout_view, name='logout'),
    path('register/', frontend_views.register, name='register'),
    # Dashboard URLs
    path('dashboard/', frontend_views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', frontend_views.admin_dashboard, name='admin_dashboard'),
    path('restaurant-admin-dashboard/', frontend_views.restaurant_admin_dashboard, name='restaurant_admin_dashboard'),
    # Password Reset URLs
    path('password-reset/', frontend_views.password_reset_request, name='password_reset'),
    path('password-reset/done/', frontend_views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', frontend_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', frontend_views.password_reset_complete, name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
