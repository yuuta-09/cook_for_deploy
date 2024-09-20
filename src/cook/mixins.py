from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def get_user_object(self):
        obj = self.get_object()
        return obj.user

    def test_func(self):
        user = self.get_user_object()
        return user == self.request.user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return render(self.request, '403.html', status=403)
        else:
            next_url = self.request.get_full_path()
            next_url = iri_to_uri(next_url)
            redirect_url = f'{settings.LOGIN_URL}?next={next_url}'
            allowed_url = url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={self.request.get_host()}
            )
            if allowed_url:
                return redirect(redirect_url)
            else:
                return redirect(settings.LOGIN_URL)
