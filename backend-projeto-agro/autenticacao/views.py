from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.middleware.csrf import get_token

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    def get(self, request):
        # Força a geração do token CSRF
        get_token(request)
        return render(request, 'login.html')

    def post(self, request):
        # Verifica se é uma requisição de API ou formulário
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            # Requisição da API
            email = request.data.get('email')
            password = request.data.get('password')
        else:
            # Requisição de formulário HTML
            email = request.POST.get('email')
            password = request.POST.get('password')

        if not email or not password:
            if 'application/json' in content_type:
                return Response(
                    {'error': 'Email e senha são obrigatórios'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return render(request, 'login.html', {'error': 'Email e senha são obrigatórios'})

        user = authenticate(username=email, password=password)
        if not user:
            if 'application/json' in content_type:
                return Response(
                    {'error': 'Credenciais inválidas'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return render(request, 'login.html', {'error': 'Credenciais inválidas'})

        # Para requisições de formulário HTML
        if 'application/json' not in content_type:
            login(request, user)
            return redirect('home')

        # Para requisições da API
        refresh = RefreshToken.for_user(user)
        response = Response({
            'token': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
        return response

@method_decorator(ensure_csrf_cookie, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 