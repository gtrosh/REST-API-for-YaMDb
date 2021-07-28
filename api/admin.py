from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "review")
    search_fields = ("text", "author", "review")
    list_filter = (
        "pub_date",
        "review",
    )
    empty_value_display = "-пусто-"


class ReviewtAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "title", "score")
    search_fields = ("text", "author", "title")
    list_filter = (
        "pub_date",
        "title",
    )
    empty_value_display = "-пусто-"


admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewtAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
