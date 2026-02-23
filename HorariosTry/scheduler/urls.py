from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.TalkCreate.as_view(), name='talk_create'),
    path('day/<int:pk>/', views.DayPrintView.as_view(), name='day_print'),
    path('success/', TemplateView.as_view(template_name="scheduler/success.html"), name='talk_success'),
]
