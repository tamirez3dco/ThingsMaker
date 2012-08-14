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
from explorer.explore.controller import Base as Controller
import explorer.tasks
import uuid
from explorer.models import Item, GhDefinition, DefinitionParam
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.utils import LazyEncoder
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop

logging.basicConfig(level=logging.INFO)

def create(request, template_name="explorer/create.html"):
    start_product = request.GET.get('start_product', None)
    product = Product.objects.get(slug=start_product)
    if product.is_variant() == False:
        logging.error('here')
        gh_def = GhDefinition.objects.filter(product=product.id)[0]
        logging.error(gh_def.file_name)
        params = DefinitionParam.objects.filter(definition=gh_def).order_by('order')
        
    return render_to_response(template_name, RequestContext(request, {'product': product, 'definition': gh_def, 'params': params, 'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def inspirations(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def mystore(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def designers(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def explore(request):
    cb = request.GET.get('callback','')
    model_types = request.GET.get('show_definitions', False)
    param_index = int(request.GET.get('param_index', 0)) 
    explore_type = request.GET.get('explore_type', 'explore')
    iterate_type = request.GET.get('iterate_type', 'linear')
    page_size = int(request.GET.get('page_size', '6'))
    material = request.GET.get('material', 'Default')
    text = request.GET.get('text', 'naama')
    #logging.error(text)
    if text == "":
        text = 'naama'
    #logging.error(text)
      
    controller = Controller(request.GET.get('distance', 'near'), material, page_size)
    start_product = request.GET.get('start_product', None)
    if (start_product):
        product = Product.objects.get(slug=start_product)
        if product.is_variant() == False:
            gh_def = GhDefinition.objects.filter(product=product.id, active=True)[0]
            if material == 'Available':
                items = controller.render_materials(['Gold', 'Silver'], None, gh_def.id, text)
            else:
                items = controller.start_iterate(gh_def.id, param_index, text)
            logging.error(gh_def.file_name)
        else:
            items = controller.explore_product(start_product, param_index, explore_type, iterate_type)
    
    else:   
        if (model_types):
            #explorer.tasks.wakeup_servers.delay(True)
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
                if material == 'Available':
                    items = controller.render_materials(['Gold', 'Silver'], item_id, None, text)
                else:
                    items = controller.explore(item_id, param_index, explore_type, iterate_type, text)
        
    #jsonp = cb + "(" + simplejson.dumps(to_json) + ");"
    jsonp = simplejson.dumps(items)
    return HttpResponse(jsonp, mimetype='text/javascript')

def add_product_variant(request):
    item_uuid = request.GET.get('item_uuid','')
    logging.error(item_uuid)
    item = Item.objects.get(uuid=item_uuid)
    controller = Controller(request.GET.get('distance', 'medium'))
    controller.item_to_product(item);
    product = Product.objects.get(pk=item.definition.product)
    #props = product.get_properties()
    slug = item_uuid
    sku = item_uuid[:30]
    price = product.price
    name = product.name
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

def get_recent_products(request):
    shop = lfs_get_object_or_404(Shop, pk=1)
    products = shop.get_recent_products()
    res = []
    for product in products:
        res.append({"image_url": product.get_item_image(), 
                    "name": product.name,
                    "price": product.price,
                    "product_url": "/product/" + product.slug,
                    "slug" : product.slug})
    result = simplejson.dumps({
        "products": res
    }, cls=LazyEncoder)

    return HttpResponse(result)    

def get_top_inspirations(request):
    shop = lfs_get_object_or_404(Shop, pk=1)
    products = shop.get_top_inspirations()
    res = []
    for product in products:
        res.append({"image_url": product.get_item_image(), 
                    "name": product.name,
                    "price": product.price,
                    "product_url": "/product/" + product.slug,
                    "slug" : product.slug})
    result = simplejson.dumps({
        "products": res
    }, cls=LazyEncoder)

    return HttpResponse(result)    