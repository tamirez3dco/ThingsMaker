import dj_database_url
DEBUG=False
STATIC_DIR_S3 = 'sitestatic'
STATIC_URL = 'http://ez3d_statics2.s3.amazonaws.com/'+STATIC_DIR_S3+'/'
DATABASES = {}
DATABASES['default'] =  dj_database_url.config()