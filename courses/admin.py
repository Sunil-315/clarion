from django.contrib import admin
from .models import Course, Lesson, UserLessonProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    readonly_fields = ('duration',)
    fields = ('order', 'title', 'video', 'duration')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_desc')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'course', 'duration')
    list_display_links = ('title',)
    list_filter = ('course',)
    list_editable = ('order',)
    readonly_fields = ('duration',)
    ordering = ['course', 'order']


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'user', 'lesson__course')
    search_fields = ('user__username', 'lesson__title')
    readonly_fields = ('completed_at',)
