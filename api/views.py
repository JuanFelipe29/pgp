from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import connection
from django.db import transaction
from rest_framework import status

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ConsultaSQLView(APIView):
    pagination_class = CustomPagination

    def get(self, request, fecha_inicio, fecha_fin):
        try:
            with connection.cursor() as cursor:
                # Utilizamos una tupla para los parámetros en la consulta SQL
                cursor.execute("""
                    SELECT DISTINCT 
                        'inserta_registro_pgp' AS funcion,
                        '901012681' AS tip_tercero,
                        p.tipoid AS tipo_doc,
                        p.identificacion AS numero_doc,
                        CASE eps.nit 
                            WHEN 551 THEN 'KS' 
                            WHEN 552 THEN 'KC' 
                        END AS documento_contrato,
                        eps.numerocontrato AS numero_contrato,
                        serv.CodigoRef AS producto,
                        '1' AS cantidad,
                        FORMAT(cit.fechadecita, 'dd/MM/yyyy') AS fecha_prestacion,
                        s.ambito,
                        aten.diagppal AS diagnostico,
                        cit.cita
                    FROM 
                        PACIENTE p,
                        EHC_EVENTODEATENCION aten,
                        EMPRESA_EPS eps,
                        CITA cit,
                        SERVICIO serv,
                        servicioxambito s
                    WHERE 
                        aten.identificacion = p.identificacion
                        AND aten.empresa = eps.nit
                        AND cit.servicio = serv.codigo
                        AND cit.beneficio = aten.beneficio
                        AND aten.empresa IN (551, 552)
                        AND aten.diagppal != 'Z532'
                        AND NOT EXISTS (
                                SELECT 1
                                FROM Reportado r
                                WHERE r.cita = cit.cita
                                AND r.estado = 1
                            )
                        AND serv.CodigoRef  = s.CodigoRef 
                        AND cit.fechadecita BETWEEN %s AND %s
                """, (fecha_inicio, fecha_fin))

                rows = cursor.fetchall()

                # Obtener la instancia de paginación
                paginator = self.pagination_class()
                paginated_data = paginator.paginate_queryset(rows, request)

                data = []
                for row in paginated_data:
                    data.append({
                        'function': row[0],
                        'tercero': row[1],
                        'tipo_doc': row[2],
                        'numero_doc': row[3],
                        'documento_contrato': row[4],
                        'numero_contrato': row[5],
                        'producto': row[6],
                        'cantidad': row[7],
                        'fecha_prestacion': row[8],
                        'ambito': row[9],
                        'diagnostico': row[10],
                        'Cita': row[11]
                    })

                return paginator.get_paginated_response(data)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
    def post(self, request):
        try:
            registros = request.data  

            with transaction.atomic():  
                for registro in registros:
                    cita = int(registro.get('cita'))
                    estado = int(registro.get('estado', 0))  
                    fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora actual

                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO Reportado (cita, estado, fecha_registro)
                            VALUES (%s, %s, %s)
                        """, (cita, estado, fecha_registro))

            return Response({'message': 'Registros insertados correctamente'}, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ListarReportadosView(APIView):
    pagination_class = CustomPagination

    def get(self, request, fecha_inicio, fecha_fin):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT 
                        p.tipoid AS tipo_doc,
                        p.identificacion AS numero_doc,
                        CASE eps.nit 
                            WHEN 551 THEN 'KS' 
                            WHEN 552 THEN 'KC' 
                        END AS documento_contrato,
                        eps.numerocontrato AS numero_contrato,
                        serv.CodigoRef AS producto,
                        '1' AS cantidad,
                        FORMAT(cit.fechadecita, 'dd/MM/yyyy') AS fecha_prestacion,
                        aten.diagppal AS diagnostico,
                        cit.cita,
                        rp.fecha_registro,
                        rp.estado
                    FROM 
                        PACIENTE p,
                        EHC_EVENTODEATENCION aten,
                        EMPRESA_EPS eps,
                        CITA cit,
                        SERVICIO serv,
                        Reportado rp
                    WHERE 
                        aten.identificacion = p.identificacion
                        AND aten.empresa = eps.nit
                        AND cit.cita = rp.cita
                        AND cit.servicio = serv.codigo
                        AND cit.beneficio = aten.beneficio
                        AND aten.empresa IN (551,552)
                        AND aten.diagppal != 'Z532'
                        AND rp.fecha_registro BETWEEN %s AND %s
                """, (fecha_inicio, fecha_fin))

                rows = cursor.fetchall()

                paginator = self.pagination_class()
                paginated_data = paginator.paginate_queryset(rows, request)

                data = []
                for row in paginated_data:
                    data.append({
                        'tipo_doc': row[0],
                        'numero_doc': row[1],
                        'documento_contrato': row[2],
                        'numero_contrato': row[3],
                        'producto': row[4],
                        'cantidad': row[5],
                        'fecha_prestacion': row[6],
                        'diagnostico': row[7],
                        'cita': row[8],
                        'fecha_registro': row[9],
                        'estado': row[10]
                    })

                return paginator.get_paginated_response(data)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
    def put(self, request):
        try:
            cita = int(request.data.get('cita'))
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Reportado
                    SET estado = 1, fecha_registro = GETDATE()
                    WHERE cita = %s
                """, (cita,))

            return Response({'message': 'Registro actualizado correctamente'}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
class ServicioXAmbitoListAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, CodigoRef, tipo, ambito, estado
                    FROM servicioxambito
                    WHERE estado = 1
                """)
                rows = cursor.fetchall()
                paginator = self.pagination_class()
                paginated_data = paginator.paginate_queryset(rows, request)
                data = []
                for row in paginated_data:
                    data.append({
                        'id': row[0],
                        'CodigoRef': row[1],
                        'tipo': row[2],
                        'ambito': row[3],
                        'estado': row[4]
                    })
                return paginator.get_paginated_response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServicioXAmbitoCreateAPIView(APIView):
    def post(self, request):
        try:
            CodigoRef = request.data.get('CodigoRef')
            tipo = request.data.get('tipo')
            ambito = request.data.get('ambito')
            estado = request.data.get('estado')
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO servicioxambito (CodigoRef, tipo, ambito, estado)
                    VALUES (%s, %s, %s, %s)
                """, (CodigoRef, tipo, ambito, estado))
            return Response({'message': 'Registro insertado correctamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServicioXAmbitoUpdateAPIView(APIView):
    def put(self, request):
        try:
            id = int(request.data.get('id'))
            CodigoRef = request.data.get('CodigoRef')
            tipo = request.data.get('tipo')
            ambito = request.data.get('ambito')
            estado = request.data.get('estado')
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE servicioxambito
                    SET CodigoRef = %s, tipo = %s, ambito = %s, estado = %s
                    WHERE id = %s
                """, (CodigoRef, tipo, ambito, estado, id))
            return Response({'message': 'Registro actualizado correctamente'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServicioXAmbitoDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, CodigoRef, tipo, ambito, estado
                    FROM servicioxambito
                    WHERE id = %s
                """, [pk])
                row = cursor.fetchone()
                if row:
                    data = {
                        'id': row[0],
                        'CodigoRef': row[1],
                        'tipo': row[2],
                        'ambito': row[3],
                        'estado': row[4]
                    }
                    return Response(data)
                else:
                    return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

