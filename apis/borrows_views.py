from rest_framework.decorators import api_view
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .validators import borrow_validators
from borrows.models import Borrow
from books.models import Book
from users.models import User


@api_view(["POST"])
def create_borrow(request):
    try:
        # validate request data
        validate_data = borrow_validators.create_borrow_validators(**request.data)
    except ValidationError as e:
        return Response(
            {
                "status": "error",
                "message": "Failed in type validation.",
                "errors": e.errors(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # check if book exists with the id
        found_book = Book.objects.get(id=validate_data.book_id)
    except Book.DoesNotExist:
        return Response(
            {"status": "error", "message": "No book found with this id"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # check if there is books in stock
    if found_book.quantity == 0:
        return Response(
            {"status": "error", "message": "Not enough books in stock."},
            status=status.HTTP_409_CONFLICT,
        )

    try:
        # check if user exists with the id
        found_user = User.objects.get(id=validate_data.user_id)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "No user found with this id"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        # create a borrow
        Borrow.objects.create(
            user_id=found_user,
            book_id=found_book,
            to_return_at=validate_data.to_return_at,
        )

        # change the quantity of books available
        found_book.quantity = found_book.quantity - 1
        found_book.save()

        return Response(
            {"status": "success", "message": "Borrow has been created."},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
