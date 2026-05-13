"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = []
from api.views import (health, home, patients, providers, appointments, availability, delete_appointment, 
                       update_appointment, login_view, register_view,patient_appointments, provider_appointments,
                       delete_patient, provider_create_appointment,update_patient,update_provider,
                       delete_provider)

urlpatterns = [
    path("", home),
    path("login/", login_view),
    path("health/", health),
    path("patients/", patients),
    path("providers/", providers),
    path("appointments/", appointments),
    path("availability/", availability),
    path("appointments/delete/<int:id>/", delete_appointment),
    path("appointments/update/<int:id>/", update_appointment),
    path('admin/', admin.site.urls),
    path("api/register/", register_view),
    path("patient-appointments/<int:user_id>/", patient_appointments),
    path("provider-appointments/<int:user_id>/", provider_appointments),
    path("patients/delete/<int:id>/", delete_patient),
    path("providers/delete/<int:id>/", delete_provider),
    path("provider-create-appointment/<int:user_id>/", provider_create_appointment),
    path("patients/update/<int:id>/", update_patient),
    path("providers/update/<int:id>/", update_provider),
]
