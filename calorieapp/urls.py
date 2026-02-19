from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path('profile_view/', views.profile_view, name='profile_view'),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add_food/", views.add_food, name="add_food"),
]




