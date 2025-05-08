from rest_framework.decorators import api_view
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .validators import borrow_validators
from borrows.models import Borrow
from books.models import Book
from users.models import User
from .serializers.serializers import BorrowSerializer
from datetime import datetime


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
            to_return_at=validate_data.to_return_at.isoformat(),
        )

        # change the quantity of books available
        found_book.quantity = found_book.quantity - 1
        found_book.save()

        return Response(
            {"status": "success", "message": "Borrow has been created."},
            status=status.HTTP_200_OK,
        )
    except Exception:
        return Response(
            {"status": "error", "message": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_borrows(request):
    try:
        # validate the queries
        book_id_raw_query = request.query_params.get("book_id")
        user_id_raw_query = request.query_params.get("user_id")
        is_returned_raw_query = request.query_params.get("is_returned")
        limit_raw_query = request.query_params.get("limit") or 10
        offset_raw_query = request.query_params.get("offset") or 0

        validate_query = borrow_validators.get_borrows_validator(
            book_id=book_id_raw_query,
            user_id=user_id_raw_query,
            is_returned=is_returned_raw_query,
            limit=limit_raw_query,
            offset=offset_raw_query,
        )
    except ValidationError as e:
        return Response(
            {
                "status": "error",
                "message": "Failed in type validation.",
                "data": e.errors(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # get the data serialize and then return to the client
        filters = {}

        if validate_query.book_id is not None:
            filters["book_id"] = validate_query.book_id

        if validate_query.user_id is not None:
            filters["user_id"] = validate_query.user_id

        if (
            validate_query.is_returned is not None
            and validate_query.is_returned == True
        ):
            filters["is_returned"] = validate_query.is_returned

        found_borrows = Borrow.objects.filter(**filters)[
            validate_query.offset : validate_query.offset + validate_query.limit
        ]

        serialized_borrow_data = BorrowSerializer(found_borrows, many=True)

        return Response(
            {
                "status": "success",
                "message": "Borrow data has been fetched.",
                "data": serialized_borrow_data.data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception:
        return Response(
            {"status": "error", "message": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT", "DELETE"])
def borrow_actions(request, id):
    try:
        # validate the url parameter id
        validate_data = borrow_validators.borrow_actions_validators(id=id)
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
        found_borrow = Borrow.objects.get(id=validate_data.id)
    except Borrow.DoesNotExist():
        return Response(
            {"status": "error", "message": "No borrow found with the id provided."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        # if the request is a get method serialize data and then send back to the user
        try:
            serialized_found_borrow = BorrowSerializer(found_borrow)

            return Response(
                {
                    "status": "success",
                    "message": "Borrow data has been fetched.",
                    "data": serialized_found_borrow.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif request.method == "PUT":
        try:
            # update to true if its none type and set to none if set to true
            if found_borrow.is_returned == False:
                found_borrow.is_returned = True
                found_borrow.save()

                return Response(
                    {
                        "status": "success",
                        "message": "Borrowed book has been returned.",
                    },
                    status=status.HTTP_200_OK,
                )
            elif found_borrow.is_returned == True:
                found_borrow.is_returned = False
                found_borrow.save()

                return Response(
                    {
                        "status": "success",
                        "message": "Borrowed book has not been returned.",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "message": "Internal server error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif request.method == "DELETE":
        # delete the found borrow
        try:
            found_borrow.delete()

            return Response(
                {"status": "success", "message": "Borrow has been returned."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
