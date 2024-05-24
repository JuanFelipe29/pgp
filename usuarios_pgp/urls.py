from django.urls import path
from .views import (
    UsuarioPgpListAPIView,
    UsuarioPgpCreateAPIView,
    UsuarioPgpUpdateAPIView,
    UsuarioPgpDetailAPIView,
    LoginAPIView
)

urlpatterns = [
    path('usuarios/', UsuarioPgpListAPIView.as_view(), name='usuario-list'),
    path('usuarios/create/', UsuarioPgpCreateAPIView.as_view(), name='usuario-create'),
    path('usuarios/<int:pk>/update/', UsuarioPgpUpdateAPIView.as_view(), name='usuario-update'),
    path('usuarios/<int:pk>/', UsuarioPgpDetailAPIView.as_view(), name='usuario-detail'),
    path('usuarios/login/', LoginAPIView.as_view(), name='usuario-login'),
]