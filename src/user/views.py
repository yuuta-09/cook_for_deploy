from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from cook.models import Recipe


# Create your views here.
class MyPageView(LoginRequiredMixin, ListView):
    models = Recipe
    context_object_name = 'recipes'
    template_name = 'user/my-page.html'
    paginate_by = 5

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)
