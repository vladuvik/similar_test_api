from celery import Celery


app = Celery('tasks', backend='redis://localhost', broker='pyamqp://')
app.autodiscover_tasks()
