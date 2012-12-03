# python imports
import os
import os.path
import imp
import socket
import djcelery
#from boto.s3.connection. import CallingFormat
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
import dj_database_url

djcelery.setup_loader()


LOCAL_HOSTNAMES= ('Amits-MacBook-Air.local',)
HOSTNAME = socket.gethostname()
#print HOSTNAME

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

def get_environment_file_path(env):
    return os.path.join(PROJECT_ROOT, 'config', '%s.py' % env)

def get_cache():
    try:
        os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS']
        os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
        os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
        return {
          'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'LOCATION': os.environ['MEMCACHIER_SERVERS'],
            'TIMEOUT': 36000,
            'BINARY': True,
          }
        }
    except:
        return {
          'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
          }
        }


if 'APP_ENV' in os.environ:
    ENV = os.environ['APP_ENV']
elif HOSTNAME in LOCAL_HOSTNAMES:
    ENV = 'development'

try:
    config = imp.load_source('env_settings', get_environment_file_path(ENV))
    from env_settings import *
except IOError:
    exit("No configuration file found for env '%s'" % ENV)


DIRNAME = os.path.dirname(__file__)


TEMPLATE_DEBUG = DEBUG
TESTING = False

DEFAULT_FROM_EMAIL = 'amit@ez3d.co'

ADMINS = (
    ('Amit Aviv', 'amit@ez3d.co'),
    ('Tamir Levy', 'tamir@ez3d.co')
)

MANAGERS = ADMINS
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en'
SITE_ID = 1
USE_I18N = True


MEDIA_ROOT = DIRNAME + "/media"
STATIC_ROOT = DIRNAME + '/sitestatic/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = 'http://ez3d_static_files.s3.amazonaws.com/sitestatic/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+0zsw5n@v7*rhl6r6ufqhoc6jlqq0f-u8c+gh(hjb+_jmg@rh6'

STATICFILES_FINDERS = (
    #'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lfs.utils.middleware.RedirectFallbackMiddleware',
    "pagination.middleware.PaginationMiddleware",
    'explorer.middleware.RequireLoginMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    "lfstheme",
    "compressor",
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    "django.contrib.admin",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.sitemaps",
    'django_countries',
    "pagination",
    'reviews',
    "tagging",
    "portlets",
    "lfs",
    "lfs.tests",
    'lfs.core',
    'lfs.caching',
    'lfs.cart',
    'lfs.catalog',
    'lfs.checkout',
    "lfs.criteria",
    "lfs.customer",
    "lfs.discounts",
    "lfs.export",
    'lfs.gross_price',
    'lfs.integrationtests',
    'lfs.mail',
    'lfs.manage',
    'lfs.marketing',
    'lfs.manufacturer',
    'lfs.net_price',
    'lfs.order',
    'lfs.page',
    'lfs.payment',
    'lfs.portlet',
    'lfs.search',
    'lfs.shipping',
    'lfs.supplier',
    'lfs.tagging',
    'lfs.tax',
    "lfs.customer_tax",
    'lfs.utils',
    'lfs.voucher',
    'lfs_contact',
    "lfs_order_numbers",
    'postal',
    'paypal.standard.ipn',
    'paypal.standard.pdt',
    'gunicorn',
    'djcelery',
    'kombu.transport.django',
    'south',
    'storages',
    'explorer',
    'social_auth'
)

FORCE_SCRIPT_NAME=""
LOGIN_URL = "/login/"
#LOGIN_REDIRECT_URL = "/manage/"
LOGIN_REDIRECT_URL = '/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'lfs.core.context_processors.main',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_login_redirect',
)

AUTHENTICATION_BACKENDS = (
    #'lfs.customer.auth.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
)

# For sql_queries
INTERNAL_IPS = (
    "127.0.0.1",
)

CACHE_MIDDLEWARE_KEY_PREFIX = "lfs"
# CACHE_BACKEND = 'file:///'
# CACHE_BACKEND = 'locmem:///'
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
#CACHE_BACKEND = 'dummy:///'

if DEBUG:
    EMAIL_HOST = ""
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
else:
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST= 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']

PAYPAL_RECEIVER_EMAIL = "info@yourbusiness.com"
PAYPAL_IDENTITY_TOKEN = "set_this_to_your_paypal_pdt_identity_token"

# TODO: Put this into the Shop model
LFS_PAYPAL_REDIRECT = True
LFS_AFTER_ADD_TO_CART = "lfs_added_to_cart"
LFS_RECENT_PRODUCTS_LIMIT = 10

LFS_ORDER_NUMBER_GENERATOR = "lfs_order_numbers.models.OrderNumberGenerator"
LFS_DOCS = "http://docs.getlfs.com/en/latest/"

LFS_INVOICE_COMPANY_NAME_REQUIRED = False
LFS_INVOICE_EMAIL_REQUIRED = True
LFS_INVOICE_PHONE_REQUIRED = True

LFS_SHIPPING_COMPANY_NAME_REQUIRED = False
LFS_SHIPPING_EMAIL_REQUIRED = False
LFS_SHIPPING_PHONE_REQUIRED = False

LFS_PRICE_CALCULATORS = [
    ['lfs.gross_price.GrossPriceCalculator', _(u'Price includes tax')],
    ['lfs.net_price.NetPriceCalculator', _(u'Price excludes tax')],
]

LFS_SHIPPING_METHOD_PRICE_CALCULATORS = [
    ["lfs.shipping.GrossShippingMethodPriceCalculator", _(u'Price includes tax')],
    ["lfs.shipping.NetShippingMethodPriceCalculator", _(u'Price excludes tax')],
]

LFS_UNITS = [
    u"l",
    u"m",
    u"qm",
    u"cm",
    u"lfm",
    u"Package",
    u"Piece",
]

LFS_PRICE_UNITS = LFS_BASE_PRICE_UNITS = LFS_PACKING_UNITS = LFS_UNITS

LFS_LOG_FILE = DIRNAME + "/../lfs.log"
LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(message)s",
            "datefmt": "%a, %d %b %Y %H:%M:%S",
        },
    },
    "handlers": {
         "console":{
            "level":"DEBUG",
            "class":"logging.StreamHandler",
            "formatter": "verbose",
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LFS_LOG_FILE,
            'mode': 'a',
        },
    },
    "loggers": {
        "default": {
            "handlers": ["logfile", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    }
}

REVIEWS_SHOW_PREVIEW = False
REVIEWS_IS_NAME_REQUIRED = False
REVIEWS_IS_EMAIL_REQUIRED = False
REVIEWS_IS_MODERATED = False

try:
    from local_settings import *
except ImportError:
    pass

###
BROKER_BACKEND = 'django'

AWS_QUERYSTRING_AUTH=False
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJ4FEEKD3KIPZASTQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_S3_SECURE_URLS=False
AWS_STORAGE_BUCKET_NAME = 'ez3d_media'

STATIC_FILES_BUCKET = 'ez3d_statics2'
BASE_MODELS_BUCKET = 'deploy_stl_Bucket'

if not DEBUG:
    STATICFILES_STORAGE = 's3utils.CachedS3BotoStorage'
    COMPRESS_STORAGE = 's3utils.CachedS3BotoStorage'
    COMPRESS_ENABLED = True
else:
    COMPRESS_ENABLED = False
    
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT

LOGIN_REQUIRED_URLS = (
#    r'/(.*)$',
)
LOGIN_REQUIRED_URLS_EXCEPTIONS = (
    r'/login(.*)$', 
    r'/logout(.*)$',
    #r'/$',
    r'/complete/(.*)',
    r'/explore',
    r'/feedback',
    #r'/explorer',
)

CACHES = get_cache()
COMPRESS_CACHE_BACKEND = 'dummy:///'



FACEBOOK_APP_ID              = '487109477988417'
FACEBOOK_API_SECRET          = '9728c8157cba4c39e5563c73b36718e8'
LINKEDIN_CONSUMER_KEY        = '2lu38tci70up'
LINKEDIN_CONSUMER_SECRET     = 'ht5O64CnmaaEbMmb'

SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_CREATE_USERS          = True
SOCIAL_AUTH_SESSION_EXPIRATION = False
FACEBOOK_EXTENDED_PERMISSIONS = ['email']

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)
