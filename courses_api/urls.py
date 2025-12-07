# courses_api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Vistas de usuario
    path('', views.index, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Vistas de cursos
    path('cursos/', views.courses_catalog, name='courses_catalog'),
    path('cursos/<slug:slug>/', views.course_detail, name='course_detail'),
    path('cursos/<slug:slug>/inscribir/', views.enroll_course, name='enroll_course'),

    # Activación de cuenta
    path('activate/<int:user_id>/', views.activate_account, name='activate'),
]