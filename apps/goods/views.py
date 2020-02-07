from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from goods import models
from django_redis import get_redis_connection
from order.models import OrderGoods


class IndexView(View):
    """首页商品展示类视图"""
    def get(self, request):
        # 获取商品种类信息
        types = models.GoodsType.objects.filter(is_delete=False)
        # 获取首页轮播商品信息表
        goods_banners = models.IndexGoodsBanner.objects.filter(is_delete=False).order_by('index')
        # 获取首页促销商品信息
        promotion_banners = models.IndexPromotionBanner.objects.all().order_by('index')
        # 获取用户购物车商品数目
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        return render(request, 'goods/index.html', locals())


class DetailView(View):
    """商品详情类视图"""
    def get(self, request, goods_id):
        try:
            goods = models.GoodsSKU.objects.filter(id=goods_id, is_delete=False).first()
        except models.GoodsSKU.DoesNotExist as e:
            return HttpResponse('该商品不存在！')
        # 获取商品分类信息
        types = models.GoodsType.objects.all()
        # 获取商品评论信息
        sku_orders = OrderGoods.objects.filter(sku=goods).exclude(comment='')
        # 获取新品信息
        new_goods = models.GoodsSKU.objects.filter(type=goods.type).order_by('-create_time')[:2]
        # 获取用户购物车中商品数目
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
            # 添加用户的历史浏览记录
            history_key = 'history_%d' % user.id
            # 先移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 将goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的五条商品信息
            conn.ltrim(history_key, 0, 4)
        return render(request, 'goods/detail.html', locals())

