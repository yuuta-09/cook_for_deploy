from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('my-page', views.MyPageView.as_view(), name='my_page'),
]
