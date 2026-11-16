"""Slow account work done in the background (see jobs app)."""
from django.core.mail import EmailMultiAlternatives
from django.tasks import task


@task
def send_email(subject, body, from_email, recipients, html_body=None):
    """Send an email after the response (retried by the job queue if the mail server fails)."""
    message = EmailMultiAlternatives(subject, body, from_email, recipients)
    if html_body:
        message.attach_alternative(html_body, 'text/html')
    message.send()
