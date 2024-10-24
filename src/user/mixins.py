from django.contrib.auth.mixins import UserPassesTestMixin


# ログイン中のユーザとユーザ更新ページのユーザが同じかどうかをチェックするMixin
class UserPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.get_object()
        return user == self.request.user
