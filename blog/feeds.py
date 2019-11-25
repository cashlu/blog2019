from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.utils.safestring import mark_safe

import markdown

from .models import Post


class LatestPostFeed(Feed):
    title = 'My blog'
    link = '/blog/'
    description = 'New posts of my blog.'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # return truncatewords(item.body, 30)
        # 处理Markdown语法，否则如果feed客户端不支持markdown语法的话，会有问题。
        return truncatewords(mark_safe(markdown.markdown(item.body)), 30)
