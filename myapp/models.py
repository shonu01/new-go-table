from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    is_customer = models.BooleanField(default=True)
    is_restaurant_admin = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
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
    opening_time = models.TimeField(default='09:00')
    closing_time = models.TimeField(default='22:00')
    max_capacity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Maximum number of guests the restaurant can accommodate"
    )
    cuisine_type = models.CharField(max_length=100, blank=True)
    price_range = models.CharField(
        max_length=20,
        choices=[
            ('$', 'Budget'),
            ('$$', 'Moderate'),
            ('$$$', 'Expensive'),
            ('$$$$', 'Luxury'),
        ],
        default='$$'
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['cuisine_type']),
        ]

    def __str__(self):
        return self.name

    def is_open(self):
        """Check if the restaurant is currently open."""
        now = timezone.now().time()
        return self.opening_time <= now <= self.closing_time

    def get_available_tables(self, date, time):
        """Get available tables for a specific date and time."""
        return self.tables.filter(
            capacity__gte=1,
            status='available'
        ).exclude(
            bookings__date=date,
            bookings__time=time,
            bookings__status__in=['pending', 'confirmed']
        )

    def get_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

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
