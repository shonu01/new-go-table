from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Restaurant, Table, Booking

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_customer', 'is_restaurant_admin', 'is_staff')
    list_filter = ('is_customer', 'is_restaurant_admin', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'is_customer', 'is_restaurant_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'is_customer', 'is_restaurant_admin')}),
    )

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'phone_number', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(admin=request.user)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'restaurant', 'capacity', 'status', 'created_at')
    list_filter = ('status', 'restaurant', 'created_at')
    search_fields = ('table_number', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant__admin=request.user)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant_name', 'table_number', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'time', 'created_at')
    search_fields = ('user__username', 'table__restaurant__name', 'table__table_number')
    readonly_fields = ('created_at', 'updated_at')
    
    def restaurant_name(self, obj):
        return obj.table.restaurant.name
    restaurant_name.short_description = 'Restaurant'
    
    def table_number(self, obj):
        return obj.table.table_number
    table_number.short_description = 'Table'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(table__restaurant__admin=request.user)
