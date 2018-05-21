import requests
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from uwcs_auth.provider import UWCSProvider


class UserProfileView(LoginRequiredMixin, View):
    template_name = ''

    def get(self, request):
        # TODO
        pass


class UWCSOauth2Adapter(OAuth2Adapter):
    provider_id = UWCSProvider.id
    access_token_url = 'https://uwcs.co.uk/o/token/'
    authorize_url = 'https://uwcs.co.uk/o/authorize/'
    profile_url = 'https://uwcs.co.uk/api/me'

    def complete_login(self, request, app, access_token, **kwargs):
        headers = {
            'Authorization': 'Bearer {0}'.format(access_token.token),
            'Content-Type': 'application/json',
        }
        extra_data = requests.get(self.profile_url, headers=headers)

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth2_login = OAuth2LoginView.adapter_view(UWCSOauth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(UWCSOauth2Adapter)
