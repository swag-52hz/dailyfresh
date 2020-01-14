import re
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from user.models import User, Address
from goods.models import GoodsSKU
from django.views import View
from django.conf import settings
from django.http import HttpResponse, Http404
from celery_tasks.tasks import send_email_task


class LoginView(View):
    def get(self, request):
        if 'username' not in request.COOKIES:
            username = ''
            checked = ''
        else:
            username = request.COOKIES.get('username')
            checked = 'checked'
        return render(request, 'user/login.html', context={
            'username': username,
            'checked': checked
        })

    def post(self, request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if not all([username, password]):
            return render(request, 'user/login.html', context={'errmsg': '用户名或密码不能为空！'})
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'user/login.html', context={'errmsg': '该用户未激活！'})
        else:
            return render(request, 'user/login.html', context={'errmsg': '用户名或密码错误！'})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('goods:index'))


class RegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password_repeat = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        if not all([username, password, password_repeat, email]):
            return render(request, 'user/register.html', context={'errmsg': '用户名、密码、确认密码、邮箱不能为空！'})
        if User.objects.filter(username=username).count():
            return render(request, 'user/register.html', context={'errmsg': '此用户名已被注册！'})
        if password != password_repeat:
            return render(request, 'user/register.html', context={'errmsg': '密码和确认密码不一致！'})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'user/register.html', context={'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'user/register.html', context={'errmsg': '请勾选用户协议！'})
        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_active = False
        user.save()
        # 加密用户身份信息，生成激活token, 默认一小时后过期
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf-8')
        # 使用celery异步发送邮件
        send_email_task.delay(username, email, token)
        return redirect(reverse('goods:index'))


class ActiveView(View):
    def get(self, request, token):
        # 进行解密，获取激活用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期！')


class UserInfoView(LoginRequiredMixin, View):
    redirect_field_name = 'next'    # 可更改url参数名，默认为next
    def get(self, request):
        address = Address.objects.get_default_address(request.user)
        # 与redis数据库建立连接
        redis_conn = get_redis_connection(alias='default')
        history_key = 'history_%d' % request.user.id
        # 获取用户最新浏览的五个商品的id
        sku_ids = redis_conn.lrange(history_key, 0, 4)
        goods_list = [ GoodsSKU.objects.get(id=id) for id in sku_ids ]
        return render(request, 'user/user_center_info.html',
                      context={
                          'page': 'info',
                          'address': address,
                          'goods_list': goods_list
                      })


class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user/user_center_order.html',
                      context={
                          'page': 'order',
                      })


class UserSiteView(LoginRequiredMixin, View):
    def get(self, request):
        address_list = Address.objects.filter(user=request.user, is_delete=False)
        return render(request, 'user/user_center_site.html',
                      context={
                          'page': 'address',
                          'address_list': address_list
                      })

    def post(self, request):
        receiver = request.POST.get('receiver', '')
        addr = request.POST.get('addr', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        is_default = request.POST.get('is_default', '')
        if not all([receiver, addr, phone]):
            return render(request, 'user/user_center_site.html',{'errmsg': '请将信息填写完整！'})
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return render(request, 'user/user_center_site.html', {'errmsg': '手机号格式错误！'})
        address = Address.objects.filter(user=request.user, is_default=True).first()
        if address and is_default:
            address.is_default = False
            address.save()
            is_default = True
        elif not address and is_default:
            is_default = True
        else:
            is_default = False
        Address.objects.create(user=request.user,
                               receiver=receiver,
                               addr=addr,
                               phone=phone,
                               zip_code=zip_code,
                               is_default=is_default)
        return redirect(reverse('user:address'))


class UserSiteEditView(View):
    def get(self, request, addr_id):
        address = Address.objects.filter(id=addr_id, user=request.user, is_delete=False).first()
        if not address:
            return Http404('您要编辑的地址不存在！')
        return render(request, 'user/user_address_edit.html',
                      context={
                          'page': 'address',
                          'address': address
                      })

    def post(self, request, addr_id):
        address = Address.objects.filter(id=addr_id, user=request.user, is_delete=False).first()
        if not address:
            return Http404('您要修改的地址不存在！')
        receiver = request.POST.get('receiver', '')
        addr = request.POST.get('addr', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        is_default = request.POST.get('is_default', '')
        if not all([receiver, addr, phone]):
            return render(request, 'user/user_center_site.html',{'errmsg': '请将信息填写完整！'})
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return render(request, 'user/user_center_site.html', {'errmsg': '手机号格式错误！'})
        default_address = Address.objects.filter(user=request.user, is_default=True).first()
        if default_address and is_default:
            default_address.is_default = False
            default_address.save()
            is_default = True
        elif not default_address and is_default:
            is_default = True
        else:
            is_default = False
        address.receiver = receiver
        address.addr = addr
        address.zip_code = zip_code
        address.phone = phone
        address.is_default = is_default
        address.save()
        return redirect(reverse('user:address'))
