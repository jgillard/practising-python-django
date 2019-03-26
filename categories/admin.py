from django.contrib import admin

from .models import Category, Question, Option, TransactionData, QuestionAnswer, MonzoUser


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    list_filter = ['parent']


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'answer_type')
    list_filter = ['category']
    inlines = [OptionInline]


class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question')
    list_filter = ['question']


class TransactionDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'category')


class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('td', 'question', 'option_answer', 'number_answer')


class MonzoUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)

admin.site.register(Question, QuestionAdmin)

admin.site.register(Option, OptionAdmin)

admin.site.register(TransactionData, TransactionDataAdmin)

admin.site.register(QuestionAnswer, QuestionAnswerAdmin)

admin.site.register(MonzoUser, MonzoUserAdmin)
