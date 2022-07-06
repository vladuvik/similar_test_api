import requests

from django.conf import settings

from population.utils import generate_pes_v3_request_payload

from similar_test_api.celery_app import app


@app.task
def generate_population_report(**kwargs):
    """
    Call external service to get population data as a response.
    Parameters
    ----------
    kwargs: data need to perform a request (radius etc.)

    Returns
    -------
    dict: response content or formatter error response if any occured
    """
    with requests.Session() as session:
        payload = generate_pes_v3_request_payload(**kwargs)
        if payload:
            try:
                response = session.post(
                    settings.SEDAC_API_URL,
                    data=payload
                )
            except requests.exceptions.RequestException as exc:
                # logger should go here
                return {
                    'message': 'error',
                    'fallback_message': str(exc)
                }
            else:
                return response.content
