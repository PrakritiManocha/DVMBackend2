from django.shortcuts import render, redirect, get_object_or_404
from .models import Train, Booking, UserProfile, Passenger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

def homepage(request):
    trains = Train.objects.all()
    current_date = timezone.now().date()
    upcoming_trains = Train.objects.filter(departure_time__date__gte=current_date).order_by('departure_time')[:5]
    return render(request, 'homepage.html', {'trains': trains})

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            return {'user_profile': user_profile}
        except UserProfile.DoesNotExist:
            return {'user_profile': None}  

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        user_profile = context.get('user_profile')

        if user_profile is None:
            return render(request, 'profile_not_found.html')  

        return self.render_to_response(context)

class SignUpView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('ticketing:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user_profile, created = UserProfile.objects.get_or_create(user=self.object, defaults={'wallet_balance': 100.0})
        return render(self.request, 'user_bookings.html', {'user_profile': user_profile})

class LoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('ticketing:homepage')

class LogoutView(LogoutView):
    next_page = reverse_lazy('ticketing:homepage')

@login_required
def user_bookings(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    bookings = Booking.objects.filter(user=request.user)

    return render(request, 'user_bookings.html', {'bookings': bookings, 'user_profile': user_profile})

@login_required
def book_ticket(request, train_id):
    selected_train = get_object_or_404(Train, pk=train_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'wallet_balance': 100.0})

    if user_profile.wallet_balance < selected_train.fare:
        messages.error(request, 'Insufficient funds. Please add money to your wallet.')
        return redirect('ticketing:user_bookings')
    elif selected_train.available_seats <= 0:
        messages.error(request, 'No available seats for the selected train.')
        return redirect('ticketing:user_bookings')
    else:
        new_booking = Booking.objects.create(
            user=request.user,
            train=selected_train,
            journey_date=selected_train.departure_time.date(),
            booking_date=timezone.now(),
        )

        passenger = Passenger.objects.create(user=request.user, name=request.user.username)
        new_booking.passengers.add(passenger)

        user_profile.wallet_balance -= selected_train.fare
        user_profile.save()

        selected_train.available_seats -= 1
        selected_train.save()

        messages.success(request, 'Ticket booked successfully!')

    return redirect('ticketing:user_bookings')

@login_required
def cancel_booking(request, booking_id):
    booking_to_cancel = get_object_or_404(Booking, pk=booking_id)

    if booking_to_cancel.train.departure_time - timezone.now() <= timezone.timedelta(hours=6):
        messages.error(request, 'Booking cannot be canceled within 6 hours of train departure.')
        return redirect('ticketing:user_bookings')

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')

    user_profile.wallet_balance += booking_to_cancel.train.fare
    user_profile.save()

    booking_to_cancel.train.available_seats += 1
    booking_to_cancel.train.save()

    booking_to_cancel.delete()

    messages.success(request, 'Booking canceled successfully!')
    return redirect('ticketing:user_bookings')
