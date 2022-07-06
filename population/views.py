from celery.result import AsyncResult

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from population.serializers import PopulationReportSerializer
from population.tasks import generate_population_report


class RetrievePopulationReportView(GenericAPIView):
    """
    View to retrieve population results from a specific task result.
    """

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('uuid')
        task = AsyncResult(task_id)
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

        return Response(
            status=status.HTTP_200_OK,
            data={
                'task': {
                    'id': task_id,
                    'status': task.status,
                },
                'result': result
            }
        )


class InitiatePopulationResultView(GenericAPIView):
    """
    View to initiate retrieval process by delay the task to process it in the background.
    """

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
