from rest_framework.decorators import api_view
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .validators import book_validators
from books.models import Book
from .serializers.serializers import BookSerializer
from borrows.models import Borrow


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


@api_view(["GET", "PUT", "DELETE"])
def books_actions(request, id):
    try:
        # validate the param
        validate_data = book_validators.books_actions_validators(id=id)
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
        # check if book exists
        found_book = Book.objects.get(id=validate_data.id)
    except Book.DoesNotExist:
        return Response(
            {"status": "error", "message": "No books were found with this id."},
            status=status.HTTP_404_NOT_FOUND,
        )
    if request.method == "GET":
        try:
            # serialize the data and send back to user
            serialized_book_data = BookSerializer(found_book)
            return Response(
                {
                    "status": "success",
                    "message": "Book data has been fetched.",
                    "data": serialized_book_data.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "PUT":
        # validate quantity
        try:
            validate_data_update = book_validators.update_book_by_id(**request.data)
        except ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Failed in type validation.",
                    "errors": e.errors(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # if the quantity is the same
        if found_book.quantity == validate_data_update.quantity:
            return Response(
                {"status": "error", "message": "No changes found in the quantity."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            # update the books
            found_book.quantity = validate_data_update.quantity
            found_book.save()

            return Response(
                {"status": "success", "message": "Book has been updated."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif request.method == "DELETE":
        # check if the books has some borrowed books
        found_borrows_by_book = Borrow.objects.filter(book_id=found_book.id)
        if len(found_borrows_by_book) > 0:
            return Response(
                {
                    "status": "error",
                    "message": f"Books has borrowed {len(found_borrows_by_book)} times.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            # delete the book
            Book.objects.filter(id=found_book.id).delete()

            return Response(
                {"status": "success", "message": "Book has been deleted."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
