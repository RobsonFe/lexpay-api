from django.urls import path
from auth.views import (
    LoginView, LogoutView, RegisterView, UserView,
    AddressView, AddressDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
    path('user/update/', UserView.as_view(), name='user_update'),
    path('user/delete/', UserView.as_view(), name='user_delete'),
    path('addresses/', AddressView.as_view(), name='addresses'),
    path('addresses/<uuid:address_id>/', AddressDetailView.as_view(), name='address_detail'),
]