# -*- coding: utf-8 -*-


from django.shortcuts import render,redirect
import logging
from django.conf import settings
from .models import *
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.db import connection
from .form import *


def global_setting(request):
    SITE_URL = settings.SITE_URL
    SITE_NAME = settings.SITE_NAME
    SITE_DESC = settings.SITE_DESC

    #分类信息获取
    category_list = Category.objects.all()

    # 文章归档数据
    # 方法三：自定义manager
    archive_list = Article.objects.distinct_date()

    # 广告数据（同学们自己完成）,这里还没有做完，有点问题，
    ad_list = Ad.objects.all()
    # 标签云数据（同学们自己完成）
    tag_list = Tag.objects.all()
    # 友情链接数据（同学们自己完成）
    link_list = Links.objects.all()
    # 文章排行榜数据（按浏览量和站长推荐的功能同学们自己完成）
    article_order_list = Article.objects.all().order_by('-click_count')
    #站长推荐
    is_recommend_list = Article.objects.all().order_by('-is_recommend')

    #评论排行\评论计数
    comment_count_list = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by('-comment_count')
    for comment_count in comment_count_list:
        print comment_count
    article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_count_list]
    return locals()


logger = logging.getLogger('blog.views')
def index(request):
    # try:
    #     file = open('aaaaaa.txt','r')
    # except Exception as e:
    #     logger.error(e)

    article_list = Article.objects.all()
    article_list = getPage(request,article_list)

    return render(request, 'index.html', locals())


def archive(request):
    try:
        year = request.GET.get('year',None)
        month = request.GET.get('month',None)
        article_list = Article.objects.filter(date_publish__icontains=year+'-'+month)
        print article_list
        article_list = getPage(request,article_list)
    except Exception as e:
            logger.error(e)
    return render(request,'archive.html',locals())

#分页代码
def getPage(request,article_list):
    paginator = Paginator(article_list,2)
    try:
        page = int(request.GET.get('page',1))
        article_list = paginator.page(page)
    except (EmptyPage,InvalidPage,PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list


def article(request):
    try:
        id = request.GET.get('id',None)
        try:
            article = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return  render(request,'failure.html', {'reason': '没有找到对应的文章'})

        comment_form = CommentForm({'author':request.user.username,
                                    'email':request.user.email,
                                    'url':request.user.url,
                                    'article':id} if request.user.is_authenticated() else{'article':id})

        comments = Comment.objects.filter(article=article).order_by('id')
        comment_list = []
        count = 0
        for comment in comments:
            print comment.content
            for item in comment_list:
                if not hasattr(item,'sub_comment'):
                    setattr(item,'sub_comment',[])
                print "item.id - ",item.id , "comment.pid - ", comment.pid
                if comment.pid == item:
                    item.sub_comment.append(comment)
                    count+=1
                    break
            if comment.pid == None:
                comment_list.append(comment)
                count+=1
    except Exception as e:
        logger.error(e)
    return render(request,'article.html',locals())

def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())

def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

def do_reg(request):
    try:
        if request.method == 'POST':
            # 注册
            reg_form = RegForm(request.POST)
            print "++++++++++++++++++++++ -->1"
            if reg_form.is_valid():
                print "++++++++++++++++++++++ -->2"
                user = User.objects.create(username=reg_form.cleaned_data['username'],
                                           email=reg_form.cleaned_data['email'],
                                           url=reg_form.cleaned_data['url'],
                                           password = make_password(reg_form.cleaned_data['password']),)
                user.save()
                #登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(request, user)
                print "++++++++++++++++++++++"
                print request.POST.get('source_url')
                print "++++++++++++++++++++++"
                return redirect(request.POST.get('source_url'))
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(request,'reg.html',locals())


def comment_post(request):
    try:
        # print request.POST
        comment_form = CommentForm(request.POST)#注意这种用法
        if comment_form.is_valid():
            comment = Comment.objects.create(username=comment_form.cleaned_data['author'],
                                             email=comment_form.cleaned_data['email'],
                                             url=comment_form.cleaned_data['url'],
                                             content=comment_form.cleaned_data['comment'],
                                             article_id=comment_form.cleaned_data['article'],
                                             user=request.user if request.user.is_authenticated() else None)
            comment.save()
        else:
            return render(request,'failure.html',{'reason':comment_form.errors})
    except Exception as e:
        logger.error(e)
    return  redirect(request.META['HTTP_REFERER'])
















