import hashlib
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View

from .forms import KeyRegistrationForm
from .models import Tier


def _get_confirm_hash(key):
    value = '{}{}{}'.format(key.key, key.email, settings.SECRET_KEY)
    return hashlib.sha256(value.encode()).hexdigest()


class RegistrationView(View):
    """
        present user with a form to fill out to get a key

        upon submission, send an email sending user to confirmation page
    """
    template_name = "simplekeys/register.html"
    default_status = 'u'
    email_subject = 'API Key Registration'
    email_message_template = 'simplekeys/confirmation_email.txt'
    from_email = settings.DEFAULT_FROM_EMAIL
    redirect = '/'

    def get(self, request):
        return render(request, self.template_name,
                      {'registration_form': KeyRegistrationForm()})

    def post(self, request):
        form = KeyRegistrationForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name,
                          {'registration_form': form})

        # go ahead w/ creation
        key = form.instance
        default_tier = getattr(settings, 'SIMPLEKEYS_DEFAULT_TIER', 'default')
        key.tier = Tier.objects.get(slug=default_tier)
        key.status = self.default_status
        key.save()

        # send email & redirect user
        confirm_hash = _get_confirm_hash(key)
        confirmation_url = (
            '{protocol}://{site}/{confirmation_url}?key={key}&email={email}'
            '&confirm={confirm_hash}').format(
                protocol='https' if request.is_secure else 'http',
                site=Site.objects.get_current().domain,
                confirmation_url='confirm', # TODO: reverse this
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


def confirmation():
    """
        present user with a simple form that just needs to be submitted
        to activate the key (don't do activation on GET to prevent
        email clients from clicking link)
    """
    pass
