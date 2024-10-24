from django.urls import path
from .views import UserListView, UserDetailView, UserUpdateView, UserDeleteView

app_name = 'user'
urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('<int:pk>', UserDetailView.as_view(), name='user_detail'),
    path('update/<int:pk>', UserUpdateView.as_view(), name='user_update'),
    path('delete/<int:pk>', UserDeleteView.as_view(), name='user_delete'),
]
