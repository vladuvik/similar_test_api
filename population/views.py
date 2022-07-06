import functools

from celery.result import AsyncResult
from django.db import transaction

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from population.serializers import PopulationReportSerializer
from population.tasks import generate_population_report


class RetrievePopulationReportView(GenericAPIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('uuid')
        task = AsyncResult(task_id)
        breakpoint()
        if not task.ready():
            return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    'task': {
                        'id': task_id,
                        'status': 'PROGRESS',

                    }
                }
            )

        result = task.get()

        breakpoint()

        return Response()


class InitiatePopulationResultView(GenericAPIView):

    permission_classes = (AllowAny,)
    serializer_class = PopulationReportSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        initiated = generate_population_report.delay(**serializer.data)

        return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    'task': {
                        'id': initiated.id,
                        'status': initiated.status,
                    }
                }
            )
