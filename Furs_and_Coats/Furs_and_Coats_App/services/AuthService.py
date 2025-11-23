from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from Furs_and_Coats_App.models import Profile


class AuthService:

    @staticmethod
    def authenticate_user(login_identifier, password):
        if not login_identifier or not login_identifier.strip():
            raise ValidationError("Email или логин обязателен для заполнения")

        if not password:
            raise ValidationError("Пароль обязателен для заполнения")

        user = None
        try:
            user = User.objects.get(email=login_identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=login_identifier)
            except User.DoesNotExist:
                raise ValidationError("Пользователь с таким email или логином не найден")

        authenticated_user = authenticate(username=user.username, password=password)
        
        if authenticated_user is None:
            raise ValidationError("Неверный пароль")

        if not authenticated_user.is_active:
            raise ValidationError("Аккаунт деактивирован")

        try:
            profile = Profile.objects.get(user=authenticated_user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=authenticated_user, phone='')

        return authenticated_user, profile

    @staticmethod
    def validate_login_data(login_identifier, password):
        errors = []

        if not login_identifier or not login_identifier.strip():
            errors.append("Email или логин обязателен для заполнения")

        if not password:
            errors.append("Пароль обязателен для заполнения")

        return errors

