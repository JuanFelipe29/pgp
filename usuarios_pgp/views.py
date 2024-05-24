from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate



class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class UsuarioPgpListAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios_pgp")
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                usuarios = [dict(zip(columns, row)) for row in rows]
                paginator = self.pagination_class()
                paginated_data = paginator.paginate_queryset(usuarios, request)
                return paginator.get_paginated_response(paginated_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UsuarioPgpCreateAPIView(APIView):
    def post(self, request):
        data = request.data
        data['clave'] = make_password(data['clave'])
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO usuarios_pgp (nombre_largo, usuario, clave, rol, estado, fecha_de_creacion)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ''',
                    [data['nombre_largo'], data['usuario'], data['clave'], data['rol'], data['estado']]
                )
                return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UsuarioPgpUpdateAPIView(APIView):
    def put(self, request, pk):
        data = request.data
        data['clave'] = make_password(data['clave'])
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE usuarios_pgp
                    SET nombre_largo = %s, usuario = %s, clave = %s, estado = %s
                    WHERE id = %s
                    ''',
                    [data['nombre_largo'], data['usuario'], data['clave'], data['estado'], pk]
                )
                return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UsuarioPgpDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios_pgp WHERE id = %s", [pk])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    usuario = dict(zip(columns, row))
                    return Response(usuario)
                else:
                    return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @property
    def pk(self):
        return self.id

    @property
    def user_id(self):
        return self.id

    def __str__(self):
        return self.username

    def get_username(self):
        return self.username


class LoginAPIView(APIView):
        def post(self, request):
            username = request.data.get('usuario')
            password = request.data.get('clave')
            
            user = authenticate(request, username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({
                    'access_token': access_token,
                    'refresh_token': str(refresh)
                }, status=status.HTTP_200_OK)
            
            return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)
        
      

