import json
from django.shortcuts import render
from django.db.models import Count
from django.views import View
from goods import models
from utils.fastdfs.client import FDFS_Client
from django.conf import settings
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map


class IndexView(View):
    def get(self, request):
        return render(request, 'admin/index/index.html')


class GoodTypeManageView(View):
    def get(self, request):
        good_types = models.GoodsType.objects.select_related('goodssku').\
            values('id', 'name', 'logo', 'image_url').annotate(num_goods = Count('goodssku')).\
            filter(is_delete=False).order_by('-num_goods', 'update_time')
        return render(request, 'admin/goods/goods_type_manage.html', locals())

class GoodTypeAddView(View):
    def get(self, request):
        return render(request, 'admin/goods/goods_type_add.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        type_name = dict_data.get('title')
        logo = dict_data.get('logo')
        image_url = dict_data.get('image_url')
        if 'http://' not in image_url:
            return to_json_data(errno=Code.DATAERR, errmsg='图片地址错误！')
        models.GoodsType.objects.create(name=type_name, logo=logo, image_url=image_url)
        return to_json_data(errmsg='商品类型添加成功！')

class GoodsTypeEditView(View):
    def get(self, request, type_id):
        goods_type = models.GoodsType.objects.filter(id=type_id).first()
        if not goods_type:
            return to_json_data(errno=Code.PARAMERR, errmsg='要删除的商品种类不存在！')
        return render(request, 'admin/goods/goods_type_add.html', locals())

    def put(self, request, type_id):
        goods_type = models.GoodsType.objects.filter(id=type_id).first()
        if not goods_type:
            return to_json_data(errno=Code.PARAMERR, errmsg='要更新的商品种类不存在！')
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        type_name = dict_data.get('title')
        logo = dict_data.get('logo')
        image_url = dict_data.get('image_url')
        if 'http://' not in image_url:
            return to_json_data(errno=Code.DATAERR, errmsg='图片地址错误！')
        goods_type.name = type_name
        goods_type.logo = logo
        goods_type.image_url = image_url
        goods_type.save()
        return to_json_data(errmsg='商品类型更新成功！')

    def delete(self, request, type_id):
        goods_type = models.GoodsType.objects.filter(id=type_id).first()
        if not goods_type:
            return to_json_data(errno=Code.PARAMERR, errmsg='要删除的商品种类不存在！')
        goods_type.is_delete = True
        goods_type.save()
        return to_json_data(errmsg='商品种类删除成功！')

class GoodsUploadImage(View):
    """上传图片至FastDFS服务器"""
    def post(self, request):
        image_file = request.FILES.get('image_file', '')
        if not image_file:
            return to_json_data(errno=Code.PARAMERR, errmsg='未选择图片！')
        if image_file.content_type not in ['image/jpg', 'image/png', 'image/jpeg', 'image/gif']:
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非图片文件！')
        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            image_ext_name = 'jpg'
        # image_file.read():读取文件
        result = FDFS_Client.upload_by_buffer(image_file.read(), image_ext_name)
        if result['Status'] == 'Upload successed.':
            image_url = settings.FASTDFS_SERVER_DOMAIN + result['Remote file_id']
            return to_json_data(data={'image_url': image_url}, errmsg='图片上传成功！')
        else:
            return to_json_data(errno=Code.UNKOWNERR, errmsg='上传图片到服务器失败！')


class GoodManageView(View):
    def get(self, request):
        goods_info = models.GoodsSKU.objects.all()
        return render(request, 'admin/goods/goods_manage.html', locals())


class GoodAddView(View):
    def get(self, request):
        return render(request, 'admin/goods/goods_add.html')