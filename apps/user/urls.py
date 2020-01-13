from django.urls import path, re_path
from . import views


app_name = 'user'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    re_path(r'active/(?P<token>.*)/', views.ActiveView.as_view(), name='active'),
    path('', views.UserInfoView.as_view(), name='info'),
    path('order/', views.UserOrderView.as_view(), name='order'),
    path('address/', views.UserSiteView.as_view(), name='address'),
    path('address/<int:addr_id>/', views.UserSiteEditView.as_view(), name='site_edit'),
]