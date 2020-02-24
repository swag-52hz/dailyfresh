from django.urls import path
from . import views


app_name = 'cart'
urlpatterns = [
    path('add/', views.AddCartView.as_view(), name='add_cart'),
    path('', views.CartInfoView.as_view(), name='info'),
    path('update/', views.UpdateCartView.as_view(), name='update'),
    path('delete/', views.DeleteCartView.as_view(), name='delete')
]