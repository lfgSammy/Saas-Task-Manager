from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username= username, password= password)
        if user:
            token, created = Token.objects.get_or_create(user= user)
            return Response({'token':token.key})
        return Response({'error':'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        if not username or not password or not email:
            return Response({'error':'All fields are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username= username).first():
            return Response({'error':'User already exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).first():
            return Response({'error':'Email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        token, created = Token.objects.get_or_create(user= user)
        return Response({'token':token.key}, status=status.HTTP_201_CREATED)
    