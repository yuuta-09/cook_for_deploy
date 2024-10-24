from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView

from cook.models import Recipe
from cook.mixins import UserPermissionMixin


# Create your views here.
class MyPageView(LoginRequiredMixin, ListView):
    models = Recipe
    context_object_name = 'recipes'
    template_name = 'user/my-page.html'
    paginate_by = 5

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

class UserListView(LoginRequiredMixin, ListView):
    models = User
    context_object_name = 'users'
    template_name = 'user/list.html'
    paginate_by = 5

    def get_queryset(self):
        return User.objects.all()

class UserDetailView(LoginRequiredMixin, DetailView):
    models = User
    context_object_name = 'user'
    template_name = 'user/detail.html'

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['pk'])

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
