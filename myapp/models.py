from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    is_customer = models.BooleanField(default=True)
    is_restaurant_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name

class Table(models.Model):
    TABLE_STATUS = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
    )
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)
    capacity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    status = models.CharField(max_length=20, choices=TABLE_STATUS, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_number} - {self.restaurant.name}"

class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    number_of_guests = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['table', 'date', 'time']

    def __str__(self):
        return f"Booking for {self.user.username} at {self.table.restaurant.name}"

    def clean(self):
        if self.date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past")
        
        # Check if table is available at the requested time
        existing_booking = Booking.objects.filter(
            table=self.table,
            date=self.date,
            time=self.time,
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.pk)
        
        if existing_booking.exists():
            raise ValidationError("This table is already booked for the selected date and time")
