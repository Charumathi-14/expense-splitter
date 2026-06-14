import secrets

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User, AuthToken
from .serializers import UserSerializer


@api_view(['GET'])
def test_api(request):
    return Response({
        'message': 'Backend Working'
    })


@api_view(['POST'])
def login(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()

    if not email or not password:
        return Response(
            {'detail': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email=email).first()

    if user and user.password != password:
        return Response(
            {'detail': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if user is None:
        user = User.objects.create(
            name=email.split('@')[0].replace('.', ' ').title(),
            email=email,
            password=password
        )

    token = AuthToken.objects.create(user=user)
    serializer = UserSerializer(user)

    return Response({
        'token': token.key,
        'user': serializer.data
    })


@api_view(['GET'])
def me(request):
    auth_header = request.headers.get('Authorization', '')
    token_key = auth_header.replace('Token ', '').strip()

    token = AuthToken.objects.filter(key=token_key).first()
    if token is None:
        return Response(
            {'detail': 'Not authenticated.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = UserSerializer(token.user)
    return Response(serializer.data)
