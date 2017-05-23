"""
    URLs only for test purposes
"""
from django.conf.urls import url
from django.contrib import admin

from simplekeys.views import RegistrationView, ConfirmationView
from . import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^example/$', views.example),
    url(r'^special/$', views.special),
    url(r'^unprotected/$', views.unprotected),
    url(r'^via_middleware/$', views.via_middleware),

    url(r'^register/$', RegistrationView.as_view()),
    url(r'^register-special/$', RegistrationView.as_view(
        tier='special',
        confirmation_url='https://confirm.example.com/special-confirm/',
    )),
    url(r'^confirm/$', ConfirmationView.as_view()),
]
