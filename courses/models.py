from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
import cloudinary
import cloudinary.api
import threading
import logging

logger = logging.getLogger(__name__)

# Configure cloudinary with Django settings
cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
    api_key=settings.CLOUDINARY_STORAGE.get('API_KEY'),
    api_secret=settings.CLOUDINARY_STORAGE.get('API_SECRET'),
)


class Course(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = CloudinaryField('image')
    short_desc = models.CharField(max_length=300)
    long_desc = models.TextField()

    def __str__(self):
        return self.title

    @property
    def total_lessons(self):
        """Total number of lessons in this course."""
        return self.lessons.count()

    def get_completed_lessons(self, user):
        """Number of completed lessons for a specific user."""
        if not user or not user.is_authenticated:
            return 0
        return UserLessonProgress.objects.filter(
            lesson__course=self,
            user=user,
            is_completed=True
        ).count()

    def get_progress_percentage(self, user):
        """Progress as a percentage (0-100) for a specific user."""
        total = self.total_lessons
        if total == 0:
            return 0
        return int((self.get_completed_lessons(user) / total) * 100)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    video = CloudinaryField('video', resource_type='video')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower = first)')
    duration = models.CharField(max_length=10, default='00:00', help_text='Duration in MM:SS format')

    class Meta:
        ordering = ['order', 'id']  # Sort by order, then by id as fallback

    def __str__(self):
        return f"{self.order}. {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get the record in DB
        # Fetch duration asynchronously to avoid blocking
        if self.video and self.duration == '00:00':
            thread = threading.Thread(target=self._fetch_and_update_duration)
            thread.start()

    def _fetch_and_update_duration(self):
        """Fetch video duration from Cloudinary and update the record."""
        try:
            logger.info(f"Fetching duration for video: {self.video.public_id}")
            resource = cloudinary.api.resource(
                self.video.public_id, 
                resource_type='video',
                image_metadata=True  # Required to get duration
            )
            total_seconds = int(resource.get('duration', 0))
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            formatted_duration = f"{minutes:02d}:{seconds:02d}"
            # Update only the duration field to avoid recursion
            Lesson.objects.filter(pk=self.pk).update(duration=formatted_duration)
            logger.info(f"Duration updated to {formatted_duration} for lesson {self.pk}")
        except Exception as e:
            logger.error(f"Error fetching video duration for lesson {self.pk}: {e}")

    def is_completed_by(self, user):
        """Check if this lesson is completed by a specific user."""
        if not user or not user.is_authenticated:
            return False
        return UserLessonProgress.objects.filter(
            lesson=self,
            user=user,
            is_completed=True
        ).exists()


class UserLessonProgress(models.Model):
    """Tracks lesson completion progress per user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name = 'User Lesson Progress'
        verbose_name_plural = 'User Lesson Progress'

    def __str__(self):
        status = '✓' if self.is_completed else '○'
        return f"{self.user.username} - {self.lesson.title} [{status}]"