from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class UserProfileManager(models.Manager):
    def create_user_profile(self, user):
        return self.create(user=user)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    objects = UserProfileManager()

    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'ticketing'


class Train(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    fare = models.DecimalField(max_digits=8, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    schedule = models.CharField(max_length=100)

class Passenger(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passengers')
    name = models.CharField(max_length=100)

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    passengers = models.ManyToManyField(Passenger, related_name='bookings')
    journey_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)
