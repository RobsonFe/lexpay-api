from auth.views import UserDeleteView
from auth.views import UserUpdateView
from django.urls import path
from auth.views import (
    LoginView, LogoutView, RegisterView, UserView,
    AddressCreateView, AddressListView, AddressUpdateView, AddressDeleteView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
    path('user/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('addresses/list/', AddressListView.as_view(), name='address_list'),
    path('addresses/create/', AddressCreateView.as_view(), name='address_create'),
    path('addresses/update/<uuid:address_id>/', AddressUpdateView.as_view(), name='address_update'),
    path('addresses/delete/<uuid:address_id>/', AddressDeleteView.as_view(), name='address_delete'),
]