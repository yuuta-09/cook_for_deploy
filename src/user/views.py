from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

from cook.models import Recipe
from user.mixins import UserPermissionMixin


# Create your views here.
class UserListView(ListView):
    models = User
    context_object_name = 'users'
    template_name = 'user/list.html'
    paginate_by = 5

    # 現在ログイン中のユーザがsuperuserでない場合はsuperuser以外のuser一覧を返す
    def get_queryset(self):
        if not self.request.user.is_superuser:
            return User.objects.exclude(is_superuser=True)

        return User.objects.all()


class UserDetailView(DetailView):
    models = User
    context_object_name = 'user'
    template_name = 'user/detail.html'

    def get_object(self):
        # 現在ログイン中のユーザがsuperuserでない場合はadminユーザだったら404を返す
        user = get_object_or_404(User, id=self.kwargs['pk'])
        if user.is_superuser and not self.request.user.is_superuser:
            raise Http404
        return user

    # ユーザとユーザのレシピをパラメータとして渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        recipes = Recipe.objects.filter(user=user)
        context['recipes'] = recipes
        return context


class UserUpdateView(UserPermissionMixin, UpdateView):
    models = User
    context_object_name = 'user'
    template_name = 'user/update.html'


class UserDeleteView(UserPermissionMixin, DeleteView):
    models = User
    context_object_name = 'user'
    template_name = 'user/delete.html'

    # HTTPメソッドgetは404を返す
    def get(self, request, *args, **kwargs):
        return render(request, '404.html')

    # POSTメソッドはユーザ削除
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect('user:user_list')
