from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from Furs_and_Coats_App.models import Profile


class RegService:

    @staticmethod
    def register_user(username, email, password, first_name, last_name, phone=None):

        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем пользователя уже существует")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")

        existing_users = User.objects.filter(email=email) | User.objects.filter(username=username)
        if existing_users.exists():
            raise ValidationError("Пользователь уже зарегистрирован")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        except Exception as e:
            raise ValidationError(f"Ошибка при создании пользователя: {str(e)}")

        try:
            profile = Profile.objects.create(
                user=user,
                phone=phone or ''
            )
        except Exception as e:

            user.delete()
            raise ValidationError(f"Ошибка при создании профиля: {str(e)}")

        return user, profile

    @staticmethod
    def validate_registration_data(username, email, password, confirm_password, first_name, last_name):
        errors = []

        if not username or not username.strip():
            errors.append("Имя пользователя обязательно для заполнения")

        if not email or not email.strip():
            errors.append("Email обязателен для заполнения")

        if not password:
            errors.append("Пароль обязателен для заполнения")

        if not first_name or not first_name.strip():
            errors.append("Имя обязательно для заполнения")

        if not last_name or not last_name.strip():
            errors.append("Фамилия обязательна для заполнения")

        if password and confirm_password and password != confirm_password:
            errors.append("Пароли не совпадают")

        if password and len(password) < 3:
            errors.append("Длина пароля должна быть больше 2")

        if email and '@' not in email:
            errors.append("Некорректный формат email")

        if username and len(username) < 3:
            errors.append("Имя пользователя должно содержать минимум 3 символа")

        return errors
