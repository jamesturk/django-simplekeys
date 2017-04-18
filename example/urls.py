from django.conf.urls import url
from django.contrib import admin

from simplekeys.views import RegistrationView, ConfirmationView
from . import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^example/$', views.example),
    url(r'^special/$', views.special),

    url(r'^register/$', RegistrationView.as_view()),
    url(r'^confirm/$', ConfirmationView.as_view()),
]
