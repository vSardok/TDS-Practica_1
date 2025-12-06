# Agregar estas funciones a courses_api/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .forms import RegistroForm
from .models import User, Course, Lesson, Enrollment, Comment
from .serializers import (
    UserSerializer, CourseSerializer, LessonSerializer,
    EnrollmentSerializer, CommentSerializer
)


def index(request):
    """Vista principal - listado de cursos inscritos"""
    if not request.user.is_authenticated:
        return redirect('login')

    app_user = _get_current_app_user(request)
    enrollments = Enrollment.objects.none()
    
    if app_user:
        enrollments = (
            Enrollment.objects
            .select_related("course", "course__instructor")
            .filter(user=app_user)
            .order_by("-enrolled_at")
        )

    return render(request, "index.html", {"enrollments": enrollments})


def course_detail(request, slug):
    """Vista de detalle de un curso específico"""
    course = get_object_or_404(
        Course.objects.select_related('instructor')
        .prefetch_related('lessons', 'comments', 'comments__user'),
        slug=slug
    )
    
    # Obtener lecciones ordenadas por posición
    lessons = course.lessons.all().order_by('position')
    
    # Calcular estadísticas del curso
    total_lessons = lessons.count()
    total_duration = sum(
        lesson.duration_sec for lesson in lessons 
        if lesson.duration_sec
    )
    
    # Convertir duración a formato legible (horas y minutos)
    hours = total_duration // 3600
    minutes = (total_duration % 3600) // 60
    
    # Obtener comentarios con rating
    comments = course.comments.filter(parent_comment__isnull=True).order_by('-created_at')
    avg_rating = course.comments.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
    rating_count = course.comments.filter(rating__isnull=False).count()
    
    # Verificar si el usuario está inscrito
    is_enrolled = False
    user_enrollment = None
    app_user = _get_current_app_user(request)
    
    if app_user:
        try:
            user_enrollment = Enrollment.objects.get(user=app_user, course=course)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    context = {
        'course': course,
        'lessons': lessons,
        'total_lessons': total_lessons,
        'total_hours': hours,
        'total_minutes': minutes,
        'comments': comments,
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'rating_count': rating_count,
        'is_enrolled': is_enrolled,
        'user_enrollment': user_enrollment,
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    """Inscribir al usuario en un curso"""
    if request.method != 'POST':
        return redirect('course_detail', slug=slug)
    
    course = get_object_or_404(Course, slug=slug)
    app_user = _get_current_app_user(request)
    
    if not app_user:
        messages.error(request, 'Debes tener un perfil completo para inscribirte.')
        return redirect('course_detail', slug=slug)
    
    # Verificar si ya está inscrito
    enrollment, created = Enrollment.objects.get_or_create(
        user=app_user,
        course=course,
        defaults={'status': 'active'}
    )
    
    if created:
        messages.success(request, f'¡Te has inscrito exitosamente en {course.title}!')
    else:
        messages.info(request, 'Ya estás inscrito en este curso.')
    
    return redirect('course_detail', slug=slug)


def courses_catalog(request):
    """Vista de catálogo de cursos disponibles"""
    courses = Course.objects.filter(status='published').select_related('instructor')
    
    # Filtros opcionales
    language = request.GET.get('language')
    search = request.GET.get('search')
    
    if language:
        courses = courses.filter(language=language)
    
    if search:
        courses = courses.filter(
            title__icontains=search
        ) | courses.filter(
            description__icontains=search
        )
    
    # Agregar estadísticas a cada curso
    for course in courses:
        course.lesson_count = course.lessons.count()
        course.student_count = course.enrollments.filter(status='active').count()
        avg_rating = course.comments.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
        course.avg_rating = round(avg_rating, 1) if avg_rating else None
    
    context = {
        'courses': courses,
        'selected_language': language,
        'search_query': search,
    }
    
    return render(request, 'courses/catalog.html', context)


def registro(request):
    """Vista de registro de usuario"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Usuario registrado correctamente')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def iniciar_sesion(request):
    """Vista de inicio de sesión"""
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        messages.error(request, 'Credenciales incorrectas')
    return render(request, 'usuarios/login.html')


@login_required
def perfil(request):
    """Vista de perfil de usuario"""
    return render(request, 'usuarios/perfil.html')


def cerrar_sesion(request):
    """Vista de cierre de sesión"""
    auth_logout(request)
    return redirect('login')


def _get_current_app_user(request):
    """Función auxiliar para obtener el usuario de la app"""
    if not request.user.is_authenticated:
        return None
    try:
        if request.user.email:
            return User.objects.get(email=request.user.email)
    except User.DoesNotExist:
        return None
    return None


# ========================================
# API VIEWSETS
# ========================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'email']
    search_fields = ['full_name', 'email']
    ordering_fields = ['full_name', 'email', 'created_at']
    ordering = ['full_name']


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'instructor', 'language']
    search_fields = ['title', 'description', 'slug']
    ordering_fields = ['title', 'created_at', 'price_usd', 'published_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        app_user = _get_current_app_user(self.request)
        if app_user is not None:
            serializer.save(instructor=app_user)
        else:
            serializer.save()


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'content_type', 'free_preview']
    search_fields = ['title']
    ordering_fields = ['course', 'position', 'title', 'created_at']
    ordering = ['course', 'position']


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'course', 'user']
    search_fields = ['course__title', 'user__full_name', 'user__email']
    ordering_fields = ['enrolled_at', 'last_accessed_at', 'progress_pct']
    ordering = ['-enrolled_at']

    def perform_create(self, serializer):
        app_user = _get_current_app_user(self.request)
        if app_user is not None:
            serializer.save(user=app_user)
        else:
            serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'user', 'rating', 'parent_comment']
    search_fields = ['body', 'course__title', 'user__full_name']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        app_user = _get_current_app_user(self.request)
        if app_user is not None:
            serializer.save(user=app_user)
        else:
            serializer.save()