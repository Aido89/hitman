from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class KeycloakOIDCBackend(OIDCAuthenticationBackend):
    """Maps Keycloak/Google claims onto Django's User model.

    Keycloak already verified the user's Google account before issuing
    these claims — we just need to create/update a local User record so
    the rest of the app (order leads, admin) can reference request.user.
    """

    def filter_users_by_claims(self, claims):
        email = claims.get('email')
        if not email:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(email__iexact=email)

    def create_user(self, claims):
        email = claims.get('email', '')
        user = self.UserModel.objects.create_user(
            username=email or claims.get('sub'),
            email=email,
        )
        self._update_user_from_claims(user, claims)
        return user

    def update_user(self, user, claims):
        self._update_user_from_claims(user, claims)
        return user

    @staticmethod
    def _update_user_from_claims(user, claims):
        user.first_name = claims.get('given_name', '') or ''
        user.last_name = claims.get('family_name', '') or ''
        user.save()
