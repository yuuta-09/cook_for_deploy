from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    posted_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="images", blank=True, null=True)
    user = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name

    def get_image_url(self):
        if self.image:
            return '/media/' + self.image.url
        else:
            return '/media/images/default.jpg'


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    amount = models.CharField(max_length=100)
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name
