"""webapp_tracet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from trigger_app import views

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.home_page),
    path("user_alert_status/", views.user_alert_status),
    path("user_alert_delete/<int:id>/", views.user_alert_delete),
    path("user_alert_create/", views.user_alert_create),
    path("event_group_log/", views.EventGroupList),
    path("test_event_group_log/", views.TestEventGroupList),
    path("event_group_details/<int:tid>/", views.EventGroup_details),
    path("event_log/", views.EventList),
    path("test_event_log/", views.TestEventList),
    path("comet_log/", views.comet_log),
    path("proposal_settings/", views.ProposalSettingsList.as_view()),
    path("observation_mwa_response/<str:id>/", views.MWAResponse),
    path("proposal_create/", views.proposal_form),
    path("proposal_edit/<int:id>/", views.proposal_form),
    path("proposal_decision_details/<int:id>/", views.ProposalDecision_details),
    path(
        "proposal_decision_result/<int:id>/<int:decision>/",
        views.ProposalDecision_result,
    ),
    path("proposal_decision_log/", views.ProposalDecisionList),
    path("proposal_decision_path/<int:id>/", views.proposal_decision_path),
    path("voevent_view/<int:id>/", views.voevent_view),
    path("event_create/", views.event_create),
    path("test_upload_xml/", views.test_upload_xml),
    path("cancel_atca_observation/<str:id>/", views.cancel_atca_observation),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
