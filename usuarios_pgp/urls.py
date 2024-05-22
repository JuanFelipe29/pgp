from django.urls import path
from .views import UsuarioPgpAPIView, LoginAPIView

urlpatterns = [
    path('usuarios/', UsuarioPgpAPIView.as_view(), name='usuario-list-create'),
    path('usuarios/login/', LoginAPIView.as_view(), name='usuario-login'),
    path('usuarios/<int:pk>/', UsuarioPgpAPIView.as_view(), name='usuario-detail'),
]
