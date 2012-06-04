# django imports
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext

import logging
from datetime import datetime
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import simplejson
from explorer.helper.server_manager import ServerManager
from django.contrib.sites.models import Site
from explorer.explore.controller import Controller
import explorer.tasks
import uuid
from explorer.models import Item
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.utils import LazyEncoder

logging.basicConfig(level=logging.INFO)

def create(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def explore(request):
    controller = Controller(request.GET.get('distance', 'medium'))
    cb = request.GET.get('callback','')
    model_types = request.GET.get('show_definitions', False)
    
    if (model_types):
        explorer.tasks.wakeup_servers.delay(True)
        items = controller.get_definitions() 
        
    else:
        start = datetime.now()
        definition_id = request.GET.get('definition_id','')
        if (definition_id != ''):
            logging.info('Start exploration')
            items = controller.start_exploration(definition_id)
            end = datetime.now()
            logging.info('Completed: '+ str(end-start))
        else:
            item_id = request.GET.get('item_id','')
            items = controller.explore(item_id)
        
    to_json = {
            "success": True,
            "items": items
    }
    jsonp = cb + "(" + simplejson.dumps(to_json) + ");"
    return HttpResponse(jsonp, mimetype='text/javascript')

def add_product_variant(request):
    item_uuid = request.POST.get('item_uuid','')
    item = Item.objects.get(uuid=item_uuid)
    controller = Controller(request.GET.get('distance', 'medium'))
    controller.item_to_product(item);
    product = Product.objects.get(pk=item.definition.product)
    #props = product.get_properties()
    slug = item_uuid
    sku = item_uuid[:30]
    price = 24.3
    name = "Vase"
    variants_count = product.variants.count()
    variant = Product(name=name, slug=slug, sku=sku, parent=product, price=price, 
                      active=True, active_images=True, active_sku=True, active_price=True, active_name=False,
                      variant_position=(variants_count + 1), sub_type=VARIANT)  
    
    variant.save()
    
    result = simplejson.dumps({
        "html": "Hi",
        "message": "Hi",
    }, cls=LazyEncoder)

    return HttpResponse(result)