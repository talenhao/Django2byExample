from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Use class-base view
from django.views.generic import ListView
# 导入表单
from .forms import EmailPostForm
# 发送邮件
from django.core.mail import send_mail
# ModelForm
from .forms import CommentForm
from .models import Comment
# tag,tag标签复用了post_list模板
from taggit.models import Tag
from django.db.models import Count


def post_list(request, tag_slug=None):
    # 获取所有的post对象
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = Post.published.filter(tags__in=[tag])
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
                  'blog/post/listold.html',
                  {'posts': posts,
                   'page': page,
                   'tag': tag})


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
    # 接收所有当前post评论
    comments = post.comments.filter(active=True)
    comment_form = CommentForm()
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


# 处理表单
def post_share(request, post_id):
    # 根据post_id取得post对象
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    # 如果提交操作且经过验证
    if request.method == "POST":
        # 表单是提交操作
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # 发送邮件
            # 创建文章
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'],
                                                                   cd['email'],
                                                                   post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,
                                                                     post_url,
                                                                     cd['name'],
                                                                     cd['comments'])
            send_mail(subject, message, 'talenhao@test.domain', [cd['to']])
            sent = True
    else:
        # 表单是显示操作
        form = EmailPostForm
    return render(request,
                  'blog/post/share.html',
                  {'form': form,
                   'post': post,
                   'sent': sent})
