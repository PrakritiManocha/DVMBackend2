from django.urls import path,include
from .views import SignUpView, homepage, user_bookings, book_ticket, cancel_booking, ProfileView, LogoutView
from django.contrib.auth import views as auth_views
from django.core.exceptions import ObjectDoesNotExist

app_name = 'ticketing'
urlpatterns = [
    path('', homepage, name='homepage'),
    path('user/bookings/', user_bookings, name='user_bookings'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('book_ticket/<int:train_id>/', book_ticket, name='book_ticket'),
    path('cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
]


