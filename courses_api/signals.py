from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from .models import User
import hashlib
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from django.conf import settings


@receiver(pre_social_login)
def create_user_on_social_login(sender, request, sociallogin, **kwargs):
    """
    Crea automáticamente un User en courses_api cuando alguien 
    inicia sesión con Google por primera vez.
    """
    # Verificar si es un nuevo usuario (no tiene cuenta Django aún)
    if sociallogin.is_existing:
        return
    
    # Obtener datos del usuario de Google
    user_data = sociallogin.account.extra_data
    email = user_data.get('email', '')
    name = user_data.get('name', '')
    
    if not email:
        return
    
    # Verificar si ya existe un User con este email en courses_api
    try:
        app_user = User.objects.get(email=email)
        # Ya existe, no hacemos nada
        return
    except User.DoesNotExist:
        # No existe, lo creamos
        pass
    
    # Crear el usuario en courses_api
    app_user = User.objects.create(
        full_name=name if name else email.split('@')[0],
        email=email,
        password_hash=hashlib.sha256(email.encode()).hexdigest(),  # Hash ficticio
        role='student'  # Por defecto es estudiante
    )
    
    print(f"✅ Usuario creado en courses_api: {app_user.full_name} ({app_user.email})")

@receiver(post_save, sender=AuthUser)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        activation_link = f"http://localhost:8500/activate/{instance.pk}/"
        subject = "Activa tu cuenta"
        message = f"Hola {instance.username},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}"

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )