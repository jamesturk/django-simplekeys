from django.shortcuts import render


def registration():
    """
        present user with a form to fill out to get a key

        upon submission, send an email sending user to confirmation page
    """
    pass


def confirmation():
    """
        present user with a simple form that just needs to be submitted
        to activate the key (don't do activation on GET to prevent
        email clients from clicking link)
    """
    pass
