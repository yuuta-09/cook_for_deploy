# Generated by Django 5.1.1 on 2024-09-28 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cook', '0002_alter_recipe_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
    ]
