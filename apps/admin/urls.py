from django.urls import path
from . import views

app_name = 'admin'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('goods_type/', views.GoodTypeManageView.as_view(), name='goods_type'),
    path('goods_type/add/', views.GoodTypeAddView.as_view(), name='goods_type_add'),
    path('goods_type/edit/<int:type_id>/', views.GoodsTypeEditView.as_view(), name='goods_type_edit'),
    path('goods/images/', views.GoodsUploadImage.as_view(), name='upload_image'),
]