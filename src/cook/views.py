from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory

from .models import Recipe, Ingredient
from .forms import RecipeForm, IngredientForm
from .mixins import AuthorRequiredMixin


# Create your views here.
class RecipeListView(ListView):
    model = Recipe
    paginate_by = 5  # ページネーションの設定
    template_name = 'recipe/list.html'
    context_object_name = 'recipes'
    ordering = ['id']


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe/detail.html'
    pk_url_kwarg = 'recipe_id'


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe/new.html'
    success_url = reverse_lazy('cook:recipe_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RecipeUpdateView(AuthorRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe/edit.html'
    pk_url_kwarg = 'recipe_id'

    def get_success_url(self):
        return reverse(
            'cook:recipe_detail',
            kwargs={'recipe_id': self.kwargs['recipe_id']}
        )


class RecipeDeleteView(AuthorRequiredMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy('cook:recipe_list')
    pk_url_kwarg = 'recipe_id'

    def get(self, request, *args, **kwargs):
        # GETリクエストには404 Not Foundを返す
        # ユーザにとってHTTPメソッドは関係がないため
        return render(request, '404.html', status=404)


class IngredientCrateView(AuthorRequiredMixin, CreateView):
    template_name = 'ingredient/new.html'
    pk_url_kwarg = 'recipe_id'
    ingredient_form = IngredientForm()

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])

    def get_success_url(self):
        return reverse(
            'cook:ingredient_detail',
            kwargs={'recipe_id': self.kwargs['recipe_id']}
        )

    def get_form_class(self):
        """
        フォームクラスの設定
        """
        form_nums = self.ingredient_form.get_num_of_forms(self.request.user.id)
        return inlineformset_factory(
            Recipe,
            Ingredient,
            form=IngredientForm,
            extra=form_nums,
            max_num=IngredientForm.max_form_num,
            can_delete=False
        )

    def adjust_form_count(self, request, adjustment):
        """
        フォームの数を調整して、材料フォームのページを表示する
        """
        current_count = self.ingredient_form.get_num_of_forms(
            self.request.user.id
        )
        redirect_url = reverse(
            "cook:ingredient_new",
            kwargs={'recipe_id': self.kwargs['recipe_id']}
        )

        new_count = current_count + adjustment
        if self.ingredient_form.is_form_num_in_range(new_count):
            # フォームの数が範囲内の場合は新たなフォームの数でセットする
            self.ingredient_form.set_num_of_forms(request.user.id, new_count)
        elif new_count > self.ingredient_form.max_form_num:
            # フォームの数が最大数を超える場合は現状のフォーム数を維持
            self.ingredient_form.set_num_of_forms(
                request.user.id, self.ingredient_form.max_form_num
            )
            redirect_url = f'{redirect_url}/?msg=これ以上フォームを増やせません。'
        elif new_count < self.ingredient_form.min_form_num:
            # フォームの数が最小数を下回る場合はデフォルトのフォーム数をセット
            self.ingredient_form.set_num_of_forms(
                request.user.id, self.ingredient_form.default_form_num
            )
            redirect_url = f'{redirect_url}/?msg=これ以上フォームを減らせません。'
        else:
            # フォームの数が予期しない数の場合はデフォルトのフォーム数をセット
            self.ingredient_form.set_num_of_forms(
                request.user.id, self.ingredient_form.default_form_num
            )
        # ユーザがリロードした際に意図しないフォームの追加を防ぐためにrenderではなくredirect
        return redirect(redirect_url)

    def get(self, request, *args, **kwargs):
        recipe = self.get_object()
        form_data = request.session.pop('form_data', None)
        form_class = self.get_form_class()
        messages = []

        # フォームの表示
        # セッションにデータが残っている場合はフォームに表示する
        if form_data:
            num_of_forms = self.ingredient_form.get_num_of_forms(
                request.user.id
            )
            form_data['ingredients-TOTAL_FORMS'] = num_of_forms
            formset = form_class(
                data=form_data,
                instance=recipe,
                queryset=Ingredient.objects.none()
            )
        else:
            formset = form_class(
                instance=recipe,
                queryset=Ingredient.objects.none()
            )

        if "msg" in self.request.GET:
            messages.append(self.request.GET.get("msg"))

        return render(request,
                      self.template_name,
                      {'form': formset, 'messages': messages}
                      )

    def post(self, request, *args, **kwargs):
        recipe = self.get_object()
        form_class = self.get_form_class()
        formset = form_class(data=request.POST, instance=recipe,
                             queryset=Ingredient.objects.none())

        if 'add_form' in request.POST:
            # フォームを追加
            request.session['form_data'] = request.POST
            request.session.modified = True
            return self.adjust_form_count(request, 1)

        elif 'remove_form' in request.POST:
            # フォームを減少
            request.session['form_data'] = request.POST
            request.session.modified = True
            return self.adjust_form_count(request, -1)

        elif 'reset_form' in request.POST:
            # フォームのリセット
            self.ingredient_form.set_num_of_forms(
                request.user.id, self.ingredient_form.default_form_num
            )
            return redirect('cook:ingredient_new', recipe.id)

        if formset.is_valid():
            formset.save()
            return redirect('cook:recipe_detail', self.kwargs['recipe_id'])
        else:
            # formset.is_validで引っかかった内容についてエラーとして表示
            return render(
                request,
                self.template_name,
                {'form': formset, 'errors': formset.errors}
            )


class IngredientUpdateView(AuthorRequiredMixin, UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'ingredient/edit.html'
    pk_url_kwarg = 'ingredient_id'

    def get_recipe_object(self):
        return self.get_object().recipe

    def get_user_object(self):
        return self.get_recipe_object().user

    def get_success_url(self):
        return reverse(
            'cook:recipe_detail',
            kwargs={'recipe_id': self.get_recipe_object().id}
        )


class IngredientDeleteView(AuthorRequiredMixin, DeleteView):
    model = Ingredient
    pk_url_kwarg = 'ingredient_id'

    def get_recipe_object(self):
        return self.get_object().recipe

    def get_user_object(self):
        return self.get_recipe_object().user

    def get_success_url(self):
        ingredient = self.get_object()
        recipe = ingredient.recipe
        return reverse(
            'cook:recipe_detail',
            kwargs={'recipe_id': recipe.id}
        )

    def get(self, request, *args, **kwargs):
        # GETリクエストは404 Not Foundを返す
        # ユーザにとってHTTPメソッドは関係がないため
        return render(request, '404.html')
