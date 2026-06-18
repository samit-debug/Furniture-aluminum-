from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = (username or kwargs.get("email") or "").strip()
        if not identifier or not password:
            return None

        UserModel = get_user_model()
        for user in self._get_users(UserModel, identifier):
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None

    def _get_users(self, UserModel, identifier):
        lookup = {"email__iexact": identifier} if "@" in identifier else {"username__iexact": identifier}
        return UserModel.objects.filter(**lookup)
