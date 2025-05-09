from rest_framework.decorators import api_view
from rest_framework.response import Response
from .validators import user_validators
from pydantic import ValidationError
from rest_framework import status
from users.models import User
import bcrypt
from .serializers import serializers
from borrows.models import Borrow


@api_view(["POST"])
def create_user(request):
    try:
        # validate req data
        validate_data = user_validators.create_user_validator(**request.data)
    except ValidationError as e:
        return Response(
            {
                "status": "error",
                "message": "Failed in type validation",
                "errors": e.errors(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

        # check duplicate values exists
    if User.objects.filter(email=validate_data.email).exists():
        return Response(
            {"status": "error", "message": "User with this email already exists."},
            status=status.HTTP_409_CONFLICT,
        )

    if User.objects.filter(phone_number=validate_data.phone_number).exists():
        return Response(
            {
                "status": "error",
                "message": "User with this phone number already exists.",
            },
            status=status.HTTP_409_CONFLICT,
        )

    try:
        # password hashing
        bytes = validate_data.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes, salt)

        # create the user
        User.objects.create(
            name=validate_data.name,
            email=validate_data.email,
            phone_number=validate_data.phone_number,
            password=hashed_password,
            membership_paid=validate_data.membership_paid,
        )

        return Response(
            {"status": "success", "message": "User has been created"},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": "Internal server error.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
def update_membership(request, id):
    try:
        # validate req id
        validate_data = user_validators.update_membership_validator(id=id)
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
        # find the user
        found_user = User.objects.get(id=validate_data.id)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "No user has been found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # if the membership is already paid
    if found_user.membership_paid == True:
        return Response(
            {"status": "error", "message": "Membership is already paid."},
            status=status.HTTP_409_CONFLICT,
        )

    try:
        # update the user
        found_user.membership_paid = True
        found_user.save()

        return Response(
            {"status": "success", "message": "User has been updated."},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": "Internal server error.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_users(request):
    try:
        # validate queries
        filter_by_raw_query = request.query_params.get("filter_by")
        limit_raw_query = request.query_params.get("limit")
        offset_raw_query = request.query_params.get("offset")

        validate_query = user_validators.get_users(
            filter_by_raw_query=filter_by_raw_query,
            limit_raw_query=limit_raw_query,
            offset_raw_query=offset_raw_query,
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
        # get data based on query and return data
        if validate_query.filter_by == "first_to_add":
            user_data = User.objects.all().order_by("created_at")[
                validate_query.offset : validate_query.offset + validate_query.limit
            ]
            serialized_user_data = serializers.UserSerializer(user_data)

            return Response(
                {
                    "status": "success",
                    "message": "User data has been fetched.",
                    "data": serialized_user_data.data,
                },
                status=status.HTTP_200_OK,
            )

        # get data based on query and return data
        elif validate_query.filter_by == "last_to_add":
            user_data = User.objects.all().order_by("-created_at")[
                validate_query.offset : validate_query.offset + validate_query.limit
            ]
            serialized_user_data = serializers.UserSerializer(user_data)

            return Response(
                {
                    "status": "success",
                    "message": "User data has been fetched.",
                    "data": serialized_user_data.data,
                },
                status=status.HTTP_200_OK,
            )

        # get data based on query and return data
        elif validate_query.filter_by == "unpaid_member":
            user_data = User.objects.filter(membership_paid=False)[
                validate_query.offset : validate_query.offset + validate_query.limit
            ]
            serialized_user_data = serializers.UserSerializer(user_data)

            return Response(
                {
                    "status": "success",
                    "message": "User data has been fetched.",
                    "data": serialized_user_data.data,
                },
                status=status.HTTP_200_OK,
            )

        # get data based if no query and return data
        user_data = User.objects.all()[
            validate_query.offset : validate_query.offset + validate_query.limit
        ]
        serialized_user_data = serializers.UserSerializer(user_data, many=True)
        return Response(
            {
                "status": "success",
                "message": "User data has been fetched.",
                "data": serialized_user_data.data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT", "DELETE"])
def user_actions(request, id):
    try:
        # validate req params
        validate_param = user_validators.update_membership_validator(id=id)
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
        # check if the data exists
        found_user = User.objects.get(id=validate_param.id)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "No user found with this id."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # if the method was get
    if request.method == "GET":
        try:
            # serialize and then send the data
            serialized_data = serializers.UserSerializer(found_user)

            return Response(
                {
                    "status": "success",
                    "message": "User data has been fetched.",
                    "data": serialized_data.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # if the method was put
    elif request.method == "PUT":
        try:
            validate_data = user_validators.UpdateUser(**request.data)
        except ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Failed in type validation.",
                    "errors": e.errors(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if the data is same as the current values
        if (
            (found_user.name == validate_data.name)
            or (found_user.email == validate_data.email)
            or (found_user.phone_number == validate_data.phone_number)
        ):
            return Response(
                {"status": "error", "message": "No changes found to update."},
                status=status.HTTP_409_CONFLICT,
            )

        # check for duplicate values
        if User.objects.filter(email=validate_data.email).exists():
            return Response(
                {"status": "error", "message": "User with this email already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        if User.objects.filter(phone_number=validate_data.phone_number).exists():
            return Response(
                {
                    "status": "error",
                    "message": "User with this phone number already exists.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            # update the user
            found_user.name = validate_data.name
            found_user.email = validate_data.email
            found_user.phone_number = validate_data.phone_number

            found_user.save()
            return Response(
                {"status": "success", "message": "User has been updated."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    # if the method is a delete
    elif request.method == "DELETE":
        # check if the user has some borrowed books
        found_borrows_by_user = Borrow.objects.filter(user_id=found_user.id)
        if len(found_borrows_by_user) > 0:
            return Response(
                {
                    "status": "error",
                    "message": f"User has {len(found_borrows_by_user)} books borrowed.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            # delete the user
            User.objects.filter(id=found_user.id).delete()

            return Response(
                {"status": "success", "message": "User has been deleted."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
