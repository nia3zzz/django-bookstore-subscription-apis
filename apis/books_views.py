from rest_framework.decorators import api_view
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .validators import book_validators
from books.models import Book


@api_view(["POST"])
def create_book(request):
    try:
        # req data validation
        validate_data = book_validators.create_book_validator(**request.data)
    except ValidationError as e:
        return Response(
            {
                "status": "error",
                "message": "Failed in type validation.",
                "errors": e.errors(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

        # check if a book with this name already exists
    if Book.objects.filter(book_name=validate_data.book_name).exists():
        return Response(
            {"status": "error", "message": "A book with this name already exists."},
            status=status.HTTP_409_CONFLICT,
        )

    try:
        # create the book
        Book.objects.create(
            book_name=validate_data.book_name,
            author_name=validate_data.author_name,
            category=validate_data.category,
            quantity=validate_data.quantity,
        )

        return Response(
            {"status": "success", "message": "A book has been created."},
            status=status.HTTP_201_CREATED,
        )
    except Exception:
        return Response(
            {"status": "error", "message": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
