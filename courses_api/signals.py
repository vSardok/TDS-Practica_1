from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from .models import User
import hashlib


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