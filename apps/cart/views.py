from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from goods.models import GoodsSKU
from django_redis import get_redis_connection


class AddCartView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0, 'errmsg':'请先登录后再添加购物车！'})
        sku_id = request.POST.get('sku_id', '')
        count = request.POST.get('count', '')
        if not all([sku_id, count]):
            return JsonResponse({'res':1, 'errmsg':'数据不全！'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res':2, 'errmsg':'商品数目错误！'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist as e:
            return JsonResponse({'res':3, 'errmsg':'商品不存在！'})
        # 进行数据库操作
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 先尝试获取购物车记录
        pre_count = conn.hget(cart_key, sku_id)
        if pre_count:
            count += int(pre_count)
        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足！'})
        conn.hset(cart_key, sku_id, count)
        # 计算用户购物车商品中的条目数
        cart_count = conn.hlen(cart_key)
        return JsonResponse({'res':5, 'message':'购物车添加成功！', 'cart_count':cart_count})


class CartInfoView(View):
    def get(self, request):
        user = request.user
        cart_key = 'cart_%d' % user.id
        conn = get_redis_connection('default')
        cart_dict = conn.hgetall(cart_key)
        skus = []
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            count = int(count)
            amount = sku.price * count
            sku.amount = amount
            sku.count = count
            skus.append(sku)
            total_count += count
            total_price += amount
        return render(request, 'cart/cart.html', locals())


class UpdateCartView(View):
    """更新购物车记录视图"""
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录后再添加购物车！'})
        sku_id = request.POST.get('sku_id', '')
        count = request.POST.get('count', '')
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不全！'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目错误！'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist as e:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在！'})
        # 进行数据库操作
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足！'})
        conn.hset(cart_key, sku_id, count)
        # 计算用户购物车中商品总件数
        vals = conn.hvals(cart_key)
        total_count = 0
        for val in vals:
            total_count += int(val)
        return JsonResponse({'res':5, 'total_count':total_count, 'message':'购物车更新成功！'})


class DeleteCartView(View):
    """删除购物车记录视图"""
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0, 'errmsg':'用户未登录！'})

        sku_id = request.POST.get('sku_id')
        if not sku_id:
            return JsonResponse({'res':1, 'errmsg':'无效的sku_id'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist as e:
            return JsonResponse({'res':2, 'errmsg':'商品不存在！'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        conn.hdel(cart_key, sku_id)
        # 计算用户购物车中商品总件数
        vals = conn.hvals(cart_key)
        total_count = 0
        for val in vals:
            total_count += int(val)
        return JsonResponse({'res':3, 'total_count':total_count, 'message':'购物车记录删除成功！'})



