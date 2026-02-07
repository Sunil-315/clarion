from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='detail'),
    path('lesson/<int:lesson_id>/toggle/', views.toggle_lesson_complete, name='toggle_lesson'),
    path('lesson/<int:lesson_id>/play/', views.LessonPlayView.as_view(), name='lesson_play'),
]
