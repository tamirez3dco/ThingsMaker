# django imports
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import os
DIRNAME = os.path.dirname(__file__)

handler500 = 'lfs.core.views.server_error'

urlpatterns = patterns("",
    (r'', include('lfs.core.urls')),
    (r'^manage/', include('lfs.manage.urls')),
)

urlpatterns += patterns("",
    (r'^reviews/', include('reviews.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^paypal/pdt/', include('paypal.standard.pdt.urls')),
)

urlpatterns += patterns("",
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(DIRNAME, "media"), 'show_indexes': True }),
)

urlpatterns += patterns("",
    (r'^create','explorer.views.create'),
    (r'^inspirations','explorer.views.inspirations'),
    (r'^mystore','explorer.views.mystore'),
    (r'^designers','explorer.views.designers'),
    (r'^explorer/add_product_variant','explorer.views.add_product_variant'),
    (r'^explorer/get_recent_products','explorer.views.get_recent_products'),
    (r'^explorer/get_top_inspirations','explorer.views.get_top_inspirations'),
    (r'^explore','explorer.views.explore'),
    (r'^addlover','explorer.views.add_lover_to_product'),
    (r'^products_by_name/(?P<name>[-\w ]*)', 'explorer.views.list_products_by_name'),    
    (r'^get_ssp/(?P<jsonstr>.*)','explorer.views.get_screened_sorted_products'),
    (r'^products_sorted/(?P<jsonstr>.*)','explorer.views.sorted_view'),

    
)
