from django.urls import path
from . import users_views, books_views, borrows_views

urlpatterns = [
    # users urls
    # create user
    path("users", users_views.create_user),
    # update membership status
    path("users/membership/<uuid:id>", users_views.update_membership),
    # get a list of users
    path("users/q", users_views.get_users),
]
