from django.shortcuts import render
from django.views import View
from goods import models


class IndexView(View):
    def get(self, request):
        # 获取商品种类信息
        types = models.GoodsType.objects.filter(is_delete=False)
        # 获取首页轮播商品信息表
        goods_banners = models.IndexGoodsBanner.objects.filter(is_delete=False).order_by('index')
        # 获取首页促销商品信息
        promotion_banners = models.IndexPromotionBanner.objects.all().order_by('index')
        return render(request, 'goods/index.html', locals())

