# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router con los viewsets existentes en tu modelo actual
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    # Nota: en Django no se usa "/" inicial en path()
    path('api/', include(router.urls)),
    path('', views.index, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
]

