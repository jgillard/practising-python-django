from django.contrib import admin

from .models import Category, Question, Option


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'answer_type')


class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question')


admin.site.register(Category, CategoryAdmin)

admin.site.register(Question, QuestionAdmin)

admin.site.register(Option, OptionAdmin)
