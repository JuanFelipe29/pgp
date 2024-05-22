from django.urls import path
from .views import ConsultaSQLView, ListarReportadosView, ServicioXAmbitoCRUD

urlpatterns = [
    path('consulta/<str:fecha_inicio>/<str:fecha_fin>/', ConsultaSQLView.as_view(), name='consulta_sql'),
    path('listar-reportados/<str:fecha_inicio>/<str:fecha_fin>/', ListarReportadosView.as_view()),
    path('insertar_reportado/', ConsultaSQLView.as_view(), name='insertar_reportado'),
    path('listar-reportados/', ListarReportadosView.as_view()),
     path('servicioxambito/', ServicioXAmbitoCRUD.as_view(), name='servicioxambito_crud'),

]