# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# --- Choices (sin tipos personalizados) ---
ROLE_CHOICES = (
    ("student", "Student"),
    ("instructor", "Instructor"),
    ("admin", "Admin"),
)

COURSE_STATUS_CHOICES = (
    ("draft", "Draft"),
    ("published", "Published"),
    ("archived", "Archived"),
)

LESSON_TYPE_CHOICES = (
    ("video", "Video"),
    ("article", "Article"),
    ("quiz", "Quiz"),
    ("file", "File"),
)

ENROLLMENT_STATUS_CHOICES = (
    ("active", "Active"),
    ("completed", "Completed"),
    ("canceled", "Canceled"),
)


class User(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="courses")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=COURSE_STATUS_CHOICES, default="draft")
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                    validators=[MinValueValidator(0)])
    language = models.CharField(max_length=20, default="es")
    thumbnail_url = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    position = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=200)
    content_url = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default="video")
    duration_sec = models.PositiveIntegerField(null=True, blank=True)
    free_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("course", "position"),)

    def __str__(self):
        return f"{self.course.title} · {self.position}. {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default="active")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    progress_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = (("user", "course"),)

    def __str__(self):
        return f"{self.user.full_name} -> {self.course.title} ({self.status})"


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    body = models.TextField()
    rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 a 5 (opcional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        snippet = (self.body[:47] + "…") if len(self.body) > 48 else self.body
        return f"{self.user.full_name} en {self.course.title}: {snippet}"
