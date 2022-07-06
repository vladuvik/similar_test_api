from django.urls import path

from population import views

app_name = "population"


urlpatterns = [
    path('init-population-report/', views.InitiatePopulationResultView.as_view(), name='init-population-report'),
    path('population-report/<uuid>/', views.RetrievePopulationReportView.as_view(), name='population-report'),
]
