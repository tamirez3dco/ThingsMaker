import urlparse
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import get_storage_class

def domain(url):
    return urlparse.urlparse(url).hostname    

class MediaFilesStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.MEDIA_FILES_BUCKET
        kwargs['custom_domain'] = domain(settings.MEDIA_URL)
        super(MediaFilesStorage, self).__init__(*args, **kwargs)

class StaticFilesStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.STATIC_FILES_BUCKET
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        super(StaticFilesStorage, self).__init__(*args, **kwargs)
        
class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.STATIC_FILES_BUCKET
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        kwargs['location'] = 'sitestatic'
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name
