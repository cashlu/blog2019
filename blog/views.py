from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


def post_list(request, tag_slug=None):
    # posts = Post.published.all()
    # return render(request, 'blog/post/list.html', {'posts': posts})
    object_list = Post.published.all()

    # 如果tag_slug不为None，获取特定tag的文章。
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 每页显示3条数据
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是一个整数，则返回第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果页数此处总页数，则返回最后一页
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html',
                  {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month,
                             publish__day=day)

    # 列出文章对应的所有活动评论
    comments = post.comments.filter(active=True)

    # 初始化一个Comment对象，后面会使用。（不初始化的话，后面else分支会提示会报错，变量没有申明。）
    new_comment = None

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # 通过表单的数据创建对象，但暂时不要保存进数据库，因为此时表单提交的数据中，
            # 没有post字段，还需要手动的关联一下。
            # 调用当前表单的save()方法生成一个Comment实例并且赋给new_comment变量。
            # save()方法仅对ModelForm生效，因为Form类没有关联到任何数据模型。
            new_comment = comment_form.save(commit=False)
            # 设置外键为本Post
            new_comment.post = post
            # 写入数据库
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 相似Tag的文章
    # 选出当前文章的所有Tag的id。
    # values_list()方法返回指定的字段的值构成的元组，通过指定flat=True，让其结果变成一个列表。
    post_tags_ids = post.tags.values_list('id', flat=True)
    # 选出具有相同tags的其他文章，排除当前文章，避免重复。
    similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # 使用Count对每个文章按照标签计数，并生成一个新字段same_tags用于存放计数的结果。（models中定义了tags的管理器）
    # 按照相同标签的数量，降序排列结果，然后截取前四个结果作为最终传入模板的数据对象。
    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    # 这里有bug，如果提交表单后，只是渲染原页面，那么刷新页面，表单会重复提交，
    # 解决的办法是提交后跳转到相应的detail页。
    return render(request, 'blog/post/detail.html',
                  {'post': post, 'comments': comments,
                   'new_comment': new_comment, 'comment_form': comment_form,
                   'similar_posts': similar_posts})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == "POST":
        # 提交表单
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # 表单验证通过
            cd = form.cleaned_data
            # 发送邮件
            # request.build_absolute_uri(post.get_absolute_url()) 返回一个完整合法的URL链接。
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{}({}) recommends you reading "{}"'.format(
                cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(
                post.title, post_url, cd['name'], cd['comments'])
            print('absolute_url = {}\npost_url = {}\nsubject = {}\nmessage = {}'
                  .format(post.get_absolute_url(), post_url, subject, message))
            send_mail(subject, message, 'cashlu@gamil.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
