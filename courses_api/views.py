from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from .forms import RegistroForm
from .models import User, Course, Lesson, Enrollment, Comment
from .serializers import (
    UserSerializer, CourseSerializer, LessonSerializer,
    EnrollmentSerializer, CommentSerializer
)


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    app_user = None
    if hasattr(request, "user") and request.user.is_authenticated and request.user.email:
        try:
            from .models import User as AppUser
            app_user = AppUser.objects.get(email=request.user.email)
        except AppUser.DoesNotExist:
            app_user = None

    enrollments = Enrollment.objects.none()
    if app_user:
        enrollments = (
            Enrollment.objects
            .select_related("course", "course__instructor")
            .filter(user=app_user)
            .order_by("-enrolled_at")
        )

    return render(request, "index.html", {"enrollments": enrollments})


def registro(request):
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
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('perfil')
        messages.error(request, 'Credenciales incorrectas')
    return render(request, 'usuarios/login.html')


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')


def cerrar_sesion(request):
    auth_logout(request)
    return redirect('login')

def _get_current_app_user(request):
    if not request.user.is_authenticated:
        return None
    try:
        if request.user.email:
            return User.objects.get(email=request.user.email)
    except User.DoesNotExist:
        return None
    return None

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

