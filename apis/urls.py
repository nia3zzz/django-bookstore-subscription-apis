from django.urls import path
from . import users_views, books_views, borrows_views

urlpatterns = [
    # users urls
    # create user
    path("users", users_views.create_user)
]
