from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get("email")
        if not identifier or not password:
            return None

        UserModel = get_user_model()
        user = self._get_user(UserModel, identifier)
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def _get_user(self, UserModel, identifier):
        lookup = {"email__iexact": identifier} if "@" in identifier else {"username__iexact": identifier}
        try:
            return UserModel.objects.get(**lookup)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            return None
