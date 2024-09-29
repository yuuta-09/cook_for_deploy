from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=50, verbose_name="レシピ名")
    description = models.TextField(verbose_name="レシピの詳細")
    posted_at = models.DateTimeField(default=timezone.now, verbose_name="投稿日")
    image = models.ImageField(
        upload_to="images", blank=True, null=True, verbose_name="レシピ画像"
    )
    user = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name="投稿ユーザー"
    )

    class Meta:
        verbose_name = "レシピ"
        verbose_name_plural = "レシピ一覧"

    def __str__(self) -> str:
        return self.name

    def get_image_url(self):
        if self.image:
            return '/media/' + self.image.url
        else:
            return '/media/images/default.jpg'


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name="材料名")
    amount = models.CharField(max_length=100, verbose_name="量")
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
        verbose_name="レシピ"
    )

    class Meta:
        verbose_name = "具材"
        verbose_name_plural = "具材一覧"

    def __str__(self) -> str:
        return self.name
