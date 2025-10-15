from django.contrib import admin

# Register your models here.
from .models import User, Course, Lesson, Comment, Enrollment

admin.site.register(User)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Comment)
admin.site.register(Enrollment)

