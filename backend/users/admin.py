from django.contrib import admin

from users.models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    """Админ зона(пользователи)."""
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
    list_editable = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    empty_value_display = '-пусто-'


class SubscriptionsAdmin(admin.ModelAdmin):
    """Админ зона(подписки)."""
    list_display = (
        'id',
        'user',
        'author',
    )
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
