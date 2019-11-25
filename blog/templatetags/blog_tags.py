from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

import markdown

from ..models import Post

register = template.Library()


# 创建一个自定义简单tag，返回Post已发布的总数。
# 如果想指定tag的名称可以在装饰器中用name属性指定。
@register.simple_tag
def total_posts():
    return Post.published.count()


# 自定义inclusion_tag，可以渲染一段HTML代码。
# latest_posts.html相当于一个HTML组件，里面的内容由show_latest_posts()方法来渲染，
# 当其他页面调用{% show_latest_posts arg %}标签的时候，则会把已经渲染好内容的
# latest_posts.html页面“嵌入”进去。
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


# comment最多的post
@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count(
        'comments')).order_by('-total_comments')[:count]


# 自定义过滤器，增加对Markdown语法的支持。
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
