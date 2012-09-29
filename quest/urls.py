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
    url(r'^admin_tools/', include('admin_tools.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(DIRNAME, "media"), 'show_indexes': True }),
)

urlpatterns += patterns("",
    (r'^create','explorer.views.create'),
    (r'^designers','explorer.views.designers'),
    (r'^explorer/add_product_variant','explorer.views.add_product_variant'),
    (r'^explorer/get_stl','explorer.views.get_stl'),
    (r'^explorer/set_product_name','explorer.views.set_product_name'),
    (r'^explore','explorer.views.explore'),
    (r'^addlover','explorer.views.add_lover_to_product'),
    (r'^products_by_name/(?P<name>[-\w ]*)', 'explorer.views.list_products_by_name'),    
    (r'^get_ssp/(?P<jsonstr>.*)','explorer.views.get_screened_sorted_products'),
    (r'^sorted_products/(?P<jsonstr>.*)','explorer.views.sorted_view'),

    
)
