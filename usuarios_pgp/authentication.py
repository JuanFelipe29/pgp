from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db import connection

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, usuario, clave FROM usuarios_pgp WHERE usuario = %s", [username])
            row = cursor.fetchone()
            if row:
                id_usuario, usuario_db, clave_db = row
                if check_password(password, clave_db):
                    return CustomUser(id=id_usuario, username=usuario_db)
        return None

    def get_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, usuario FROM usuarios_pgp WHERE id = %s", [user_id])
            row = cursor.fetchone()
            if row:
                id_usuario, usuario_db = row
                return CustomUser(id=id_usuario, username=usuario_db)
        return None

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
