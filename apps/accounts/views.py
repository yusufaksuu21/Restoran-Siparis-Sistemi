from __future__ import annotations

from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, UserMeSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class MeView(APIView):
    def get(self, request):
        return response.Response(UserMeSerializer(request.user).data)

    def patch(self, request):
        ser = UserMeSerializer(instance=request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(ser.data)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


__all__ = ["RegisterView", "MeView", "LoginView", "TokenRefreshView"]

