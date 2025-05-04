from rest_framework.decorators import api_view
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .validators import book_validators
from books.models import Book
from .serializers.serializers import BookSerializer


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


@api_view(["GET"])
def get_books(request):
    try:
        # validate the queries
        category_raw_query = request.query_params.get("category")
        author_name_raw_query = request.query_params.get("author_name")
        limit_raw_query = request.query_params.get("limit") or 10
        offset_raw_query = request.query_params.get("offset") or 0

        validate_query = book_validators.get_books_query_validators(
            category=category_raw_query,
            author_name=author_name_raw_query,
            limit=limit_raw_query,
            offset=offset_raw_query,
        )

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
        # get data based on query and return it
        filters = {}

        if validate_query.author_name is not None:
            filters["author_name"] = validate_query.author_name

        if validate_query.category is not None:
            filters["category"] = validate_query.category

        book_data = Book.objects.filter(**filters)[
            validate_query.offset : validate_query.offset + validate_query.limit
        ]

        # serialize the data
        serialized_books_data = BookSerializer(book_data, many=True)

        return Response(
            {
                "status": "success",
                "message": "Books data have been fetched.",
                "data": serialized_books_data.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
