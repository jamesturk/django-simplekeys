import hashlib
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template import loader
from django.views.generic import View
from django.http import HttpResponseBadRequest

from .forms import KeyRegistrationForm, KeyConfirmationForm
from .models import Tier, Key


def _get_confirm_hash(key, email):
    value = '{}{}{}'.format(key, email, settings.SECRET_KEY)
    return hashlib.sha256(value.encode()).hexdigest()


class RegistrationView(View):
    """
        present user with a form to fill out to get a key

        upon submission, send an email sending user to confirmation page
    """
    template_name = "simplekeys/register.html"
    email_subject = 'API Key Registration'
    email_message_template = 'simplekeys/confirmation_email.txt'
    from_email = settings.DEFAULT_FROM_EMAIL
    tier = 'default'
    redirect = '/'
    confirmation_url = '/confirm/'

    def get(self, request):
        return render(request, self.template_name,
                      {'form': KeyRegistrationForm()})

    def post(self, request):
        form = KeyRegistrationForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name,
                          {'form': form})

        # go ahead w/ creation
        key = form.instance
        key.tier = Tier.objects.get(slug=self.tier)
        # TODO: option to override this and avoid sending email?
        key.status = 'u'
        key.save()

        # send email & redirect user
        confirm_hash = _get_confirm_hash(key.key, key.email)

        # if URL is relative, make absolute
        if not self.confirmation_url.startswith(('http:', 'https:')):
            confirmation_url = '{protocol}://{site}{confirmation_url}'.format(
                protocol='https' if request.is_secure else 'http',
                site=Site.objects.get_current().domain,
                confirmation_url=self.confirmation_url
            )
        else:
            confirmation_url = self.confirmation_url

        confirmation_url = (
            '{base}?key={key}&email={email}&confirm_hash={confirm_hash}'
        ).format(
            base=confirmation_url,
            key=key.key,
            email=key.email,
            confirm_hash=confirm_hash
        )
        message = loader.render_to_string(
            self.email_message_template,
            {'key': key, 'confirmation_url': confirmation_url}
        )

        send_mail(self.email_subject,
                  message,
                  self.from_email,
                  [key.email])

        return redirect(self.redirect)


class ConfirmationView(View):
    """
        present user with a simple form that just needs to be submitted
        to activate the key (don't do activation on GET to prevent
        email clients from clicking link)
    """

    confirmation_template_name = "simplekeys/confirmation.html"
    confirmed_template_name = "simplekeys/confirmed.html"

    def get(self, request):
        form = KeyConfirmationForm(request.GET)
        if form.is_valid():
            return render(request, self.confirmation_template_name,
                          {'form': form})
        else:
            return HttpResponseBadRequest('invalid request')

    def post(self, request):
        form = KeyConfirmationForm(request.POST)
        if form.is_valid():
            hash = _get_confirm_hash(form.cleaned_data['key'],
                                     form.cleaned_data['email'])
            if hash != form.cleaned_data['confirm_hash']:
                return HttpResponseBadRequest('invalid request')

            # update the key
            try:
                key = Key.objects.get(key=form.cleaned_data['key'],
                                      status='u')
            except Key.DoesNotExist:
                return HttpResponseBadRequest('invalid request')

            key.status = 'a'
            key.save()
            return render(request, self.confirmed_template_name, {'key': key})
        else:
            return HttpResponseBadRequest('invalid request')
