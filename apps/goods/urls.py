from django.urls import path
from . import views


app_name = 'goods'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('detail/<int:goods_id>/', views.DetailView.as_view(), name='detail'),
]