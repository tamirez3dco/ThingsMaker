# python imports
import locale
import sys
import traceback

# django imports
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext
from django.utils import simplejson
from django.core.mail import send_mail

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop

# Load logger
import logging
logger = logging.getLogger("default")


def shop_view(request, template_name="lfs/shop/shop.html"):
    """Displays the shop.
    """
    print "static url %s" % settings.STATIC_URL
    shop = lfs_get_object_or_404(Shop, pk=1)
    return render_to_response(template_name, RequestContext(request, {
        "shop": shop
    }))

def lfs_feedback(request):
    name = request.POST.get('name', "")
    emailAddr = request.POST.get('email', settings.ADMINS[0][1])
    message = request.POST.get('message', "No Message")
    to_emails = [a[1] for a in settings.ADMINS]
    send_mail('Feedback from %s' % name, message, emailAddr, to_emails)
    result = "success"
    return HttpResponse(result)

def server_error(request):
    """Own view in order to pass RequestContext and send an error message.
    """
    exc_type, exc_info, tb = sys.exc_info()
    response = "%s\n" % exc_type.__name__
    response += "%s\n" % exc_info
    response += "TRACEBACK:\n"
    for tb in traceback.format_tb(tb):
        response += "%s\n" % tb

    if request.user:
        response += "User: %s\n" % request.user.username

    response += "\nREQUEST:\n%s" % request

    try:
        from_email = settings.ADMINS[0][1]
        to_emails = [a[1] for a in settings.ADMINS]
    except IndexError:
        pass
    else:
        mail = EmailMessage(
            subject="Error LFS", body=response, from_email=from_email, to=to_emails)
        mail.send(fail_silently=True)

    t = loader.get_template('500.html')
    return HttpResponse(t.render(RequestContext(request)), status=500)


def one_time_setup():
    shop = lfs_get_object_or_404(Shop, pk=1)
    try:
        locale.setlocale(locale.LC_ALL, str(shop.default_locale))
    except locale.Error, e:
        logger.error("Unsupported locale in LMI/Preferences/Default Values/Default Shop Locale: '%s'." % shop.default_locale)
