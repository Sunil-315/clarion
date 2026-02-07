from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Course, Lesson, UserLessonProgress


@login_required
@require_POST
def toggle_lesson_complete(request, lesson_id):
    """Toggle the is_completed status of a lesson via AJAX for the current user."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Get or create progress record for this user/lesson
    progress, created = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    # Toggle completion status
    progress.is_completed = not progress.is_completed
    progress.completed_at = timezone.now() if progress.is_completed else None
    progress.save()
    
    # Return updated progress for frontend
    course = lesson.course
    return JsonResponse({
        'success': True,
        'is_completed': progress.is_completed,
        'progress_percentage': course.get_progress_percentage(request.user),
        'completed_lessons': course.get_completed_lessons(request.user),
        'total_lessons': course.total_lessons,
    })


def home(request):
    """Home page with featured courses."""
    courses = Course.objects.all()[:3]  # Show up to 3 courses on home
    return render(request, 'home.html', {'courses': courses})


class CourseListView(ListView):
    """Display all courses with thumbnail, title, and short description."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'


class CourseDetailView(LoginRequiredMixin, DetailView):
    """Display full course details including long description. Login required."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        # Add user-specific progress data
        context['completed_lessons'] = course.get_completed_lessons(user)
        context['progress_percentage'] = course.get_progress_percentage(user)

        # Add completion status for each lesson
        lessons_with_status = []
        for lesson in course.lessons.all():
            lessons_with_status.append({
                'lesson': lesson,
                'is_completed': lesson.is_completed_by(user)
            })
        context['lessons_with_status'] = lessons_with_status

        return context


class LessonPlayView(LoginRequiredMixin, DetailView):
    """Display video player for a specific lesson. Login required."""
    model = Lesson
    template_name = 'courses/lesson_play.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context
