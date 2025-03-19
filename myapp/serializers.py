from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Restaurant, Table, Booking
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'is_customer', 'is_restaurant_admin')
        read_only_fields = ('id',)

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class TableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Table
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    restaurant_name = serializers.CharField(source='table.restaurant.name', read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'status')

    def validate(self, data):
        if data['date'] < timezone.now().date():
            raise serializers.ValidationError("Booking date cannot be in the past")
        
        # Check if table is available at the requested time
        existing_booking = Booking.objects.filter(
            table=data['table'],
            date=data['date'],
            time=data['time'],
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if existing_booking.exists():
            raise serializers.ValidationError("This table is already booked for the selected date and time")
        
        return data 