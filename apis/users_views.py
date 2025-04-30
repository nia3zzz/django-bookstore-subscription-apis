from rest_framework.decorators import api_view
from rest_framework.response import Response
from .validators import user_validators
from pydantic import ValidationError
from rest_framework import status
from users.models import User
import bcrypt


@api_view(["POST"])
def create_user(request):
    try:
        # validate req data
        validate_data = user_validators.create_user_validator(**request.data)

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
            status=status.HTTP_200_OK,
        )

    except ValidationError as e:
        return Response(
            {
                "status": "error",
                "message": "Failed in type validation",
                "errors": e.errors(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": "Internal server error.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
