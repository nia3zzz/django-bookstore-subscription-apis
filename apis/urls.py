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
    # user action using an id
    path("users/<uuid:id>", users_views.user_actions),
    # books urls
    # create book
    path("books", books_views.create_book),
    # get a list of books through query filtering
    path("books/q", books_views.get_books),
    # books actions by id
    path("books/<uuid:id>", books_views.books_actions),
]
