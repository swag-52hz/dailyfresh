from django.urls import path
from . import views


app_name = 'cart'
urlpatterns = [
    path('add/', views.AddCartView.as_view(), name='add_cart'),
]