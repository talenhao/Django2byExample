from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Use class-base view
from django.views.generic import ListView


def post_list(request):
    # 获取所有的post对象
    object_list = Post.published.all()
    # 以每页3篇post初始化paginator对象实例
    paginator = Paginator(object_list, 3)
    # 获取当前所处页数.从页面传递过来一个"page"
    page = request.GET.get('page')

    try:
        # 获取当前页的posts对象
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果返回page页数不足1,即非整数,只显示一页即第一页
        posts = paginator.page(1)
    except EmptyPage:
        # if page is empty, disable the lastest page
        posts = paginator.page(paginator.num_pages)

    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'paginator': paginator})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
