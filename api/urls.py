from django.urls import path
from .views import ConsultaSQLView, ListarReportadosView,ServicioXAmbitoListAPIView,ServicioXAmbitoCreateAPIView,ServicioXAmbitoUpdateAPIView,ServicioXAmbitoDetailAPIView

urlpatterns = [
    path('consulta/<str:fecha_inicio>/<str:fecha_fin>/', ConsultaSQLView.as_view(), name='consulta_sql'),
    path('listar-reportados/<str:fecha_inicio>/<str:fecha_fin>/', ListarReportadosView.as_view()),
    path('insertar_reportado/', ConsultaSQLView.as_view(), name='insertar_reportado'),
    path('listar-reportados/', ListarReportadosView.as_view()),
    path('servicioxambito/', ServicioXAmbitoListAPIView.as_view(), name='servicioxambito-list'),
    path('servicioxambito/create/', ServicioXAmbitoCreateAPIView.as_view(), name='servicioxambito-create'),
    path('servicioxambito/<int:pk>/update/', ServicioXAmbitoUpdateAPIView.as_view(), name='servicioxambito-update'),
    path('servicioxambito/<int:pk>/', ServicioXAmbitoDetailAPIView.as_view(), name='servicioxambito-detail'),

]