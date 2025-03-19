from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Restaurant, Table, Booking

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_customer', 'is_restaurant_admin')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer', 'is_restaurant_admin', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'cuisine_type', 'price_range', 'get_rating', 'is_active')
    list_filter = ('is_active', 'cuisine_type', 'price_range')
    search_fields = ('name', 'address', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone_number', 'email')
        }),
        ('Business Details', {
            'fields': ('opening_time', 'closing_time', 'max_capacity', 'cuisine_type', 'price_range')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_rating(self, obj):
        rating = obj.get_rating()
        if rating:
            return format_html(
                '<span style="color: #ffc107;">★</span> {:.1f}',
                rating
            )
        return 'No ratings'
    get_rating.short_description = 'Rating'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'restaurant', 'capacity', 'status')
    list_filter = ('status', 'restaurant', 'capacity')
    search_fields = ('table_number', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Table Information', {
            'fields': ('restaurant', 'table_number', 'capacity', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('get_restaurant', 'user', 'date', 'time', 'number_of_guests', 'status')
    list_filter = ('status', 'date', 'time')
    search_fields = ('user__username', 'user__email', 'table__restaurant__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'table', 'date', 'time', 'number_of_guests', 'status', 'special_requests')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_restaurant(self, obj):
        return obj.table.restaurant.name
    get_restaurant.short_description = 'Restaurant'
    get_restaurant.admin_order_field = 'table__restaurant__name'
