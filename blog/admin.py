from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status',)
    list_filter = ('status', 'created', 'publish', 'author',)
    search_fields = ('title', 'body',)
    # 自动生成slug字段，生成的组成部分是title字段。
    prepopulated_fields = {'slug': ('title',)}
    # django默认的外键的admin控件是下拉菜单，raw_id_fields可以将其修改为弹出对话框选择或搜索的方式，填入的是主键。
    raw_id_fields = ('author',)
    # 时间层级导航条
    date_hierarchy = 'publish'
    ordering = ('status', 'publish',)

