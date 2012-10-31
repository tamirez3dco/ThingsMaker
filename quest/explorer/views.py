# django imports
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import loader
from django.template import RequestContext
from django.core.cache import cache
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
        gh_def = GhDefinition.objects.filter(product=product.id, active=True)[0]
        logging.error(gh_def.file_name)
    else:
        item = Item.objects.filter(uuid=start_product)[0]
        gh_def = item.definition 

    params = DefinitionParam.objects.filter(definition=gh_def, active=True).order_by('order')
        
    return render_to_response(template_name, RequestContext(request, {'product': product, 'definition': gh_def, 'params': params, 'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def inspirations(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def mystore(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def designers(request, template_name="explorer/create.html"):
    return render_to_response(template_name, RequestContext(request, {'site_domain': Site.objects.get(id=settings.SITE_ID).domain}))

def explore(request):
    #cb = request.GET.get('callback','')
    model_types = request.GET.get('show_definitions', False)
    param_index = int(request.GET.get('param_index', 0)) 
    explore_type = request.GET.get('explore_type', 'explore')
    iterate_type = request.GET.get('iterate_type', 'linear')
    page_size = int(request.GET.get('page_size', '6'))
    material = request.GET.get('material', 'Default')
    text = request.GET.get('text', '')
    text = text.strip()
      
    controller = Controller(request.GET.get('distance', 'near'), material, page_size)
    start_product = request.GET.get('start_product', None)
    if (start_product):
        product = Product.objects.get(slug=start_product)
        if product.is_variant() == False:
            gh_def = GhDefinition.objects.filter(product=product.id, active=True)[0]
            if material == 'Available':
                #material_list = DefinitionMaterial.
                items = controller.render_materials(['Gold', 'Silver'], None, gh_def.id, text)
            else:
                items = controller.get_random_items(product)
                #items = controller.start_iterate(gh_def.id, param_index, text)
            logging.error(gh_def.file_name)
        else:
            if material == 'Available':
                items = controller.render_materials(['Gold', 'Silver'], start_product, None, text)
            else:
                items = controller.explore(start_product, param_index, explore_type, iterate_type, text)            
            #items = controller.explore_product(start_product, param_index, explore_type, iterate_type)
    
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

def add_lover_to_product(request):
    item_uuid = request.POST.get('item_uuid','')
    item = Item.objects.get(uuid=item_uuid)
    product = Product.objects.get(slug=item_uuid)
    product.increase_product_lovers()
    result = simplejson.dumps({
        "html": "Hi",
        "message": "Hi",
    }, cls=LazyEncoder)
    return HttpResponse(result)

def set_product_name(request):  
    result = simplejson.dumps({
        "html": "Hi",
        "message": "Hi",
    }, cls=LazyEncoder)    
    new_name = request.GET.get('new_name','') 
    if new_name == "":
        return HttpResponse(result)
    
    slug = request.GET.get('slug','') 
    p = Product.objects.get(slug=slug)
    p.name = new_name
    p.active_name = True
    p.save()
    return HttpResponse(result)

def add_product_variant(request):
    result = simplejson.dumps({
        "html": "Hi",
        "message": "Hi",
    }, cls=LazyEncoder)
    item_uuid = request.GET.get('item_uuid','')
    logging.error(item_uuid)
    item = Item.objects.get(uuid=item_uuid)
    old_products = Product.objects.filter(slug=item.uuid)
    if len(old_products)>0:
        return HttpResponse(result)
    controller = Controller(request.GET.get('distance', 'medium'))
    controller.item_to_product(item);
    product = Product.objects.get(pk=item.definition.product)
    #props = product.get_properties()
    slug = item_uuid
    sku = item_uuid[:30]
    price = product.price
    name = product.name
    variants_count = product.variants.count()
    variant = Product(name=name, slug=slug, sku=sku, parent=product, price=price, item=item, 
                      active=True, active_images=True, active_sku=True, active_price=True, active_name=False,
                      variant_position=(variants_count + 1), sub_type=VARIANT)  
    
    variant.save()
    return HttpResponse(result)

def list_products_by_name(request, name, template_name="lfs/catalog/products/products_by_name.html"):
    raw_products = Product.objects.filter(sub_type = VARIANT, name=name, active=True).order_by('-stock_amount')
    products = []
    for product in raw_products:
        products.append({
            "image_url": product.get_item_image(),            
            "name": product.name,
            "price": product.price,
            "product_url": "/product/" + product.slug
        })
    result = render_to_response(template_name, RequestContext(request, {
            "products": raw_products
    }))
    return result

#def sorted_view(request, jsonstr, template_name="lfs/catalog/products/all_products_sorted.html"):
#    print "thats me sorted_view"
#    myobj = simplejson.loads(jsonstr)
#    cache_key = "%s-sorted-view-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, jsonstr)
#    #result = cache.get(cache_key)
#    if result is not None:
#        return result
#    shop = lfs_get_object_or_404(Shop, pk=1)
#    myobj["shop"]=shop
#    #logging.error(myobj["myname"])
#    result = render_to_string(template_name, RequestContext(request, myobj))
#    #cache.set(cache_key, result, 3600)
#    return result
def sorted_view(request, jsonstr, template_name="lfs/catalog/products/all_products_sorted.html"):
    print "jsonstr-- %s --" % jsonstr
    myobj = simplejson.loads(jsonstr)
    shop = lfs_get_object_or_404(Shop, pk=1)
    myobj["shop"]=shop
    return render_to_response(template_name, RequestContext(request, myobj))

def get_screened_sorted_products(request,jsonstr):
    #print "thats me ssp"
    cache_key = "%s-sorted-prods-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, jsonstr)
    result = cache.get(cache_key)
    #print cache_key
    #print result
    if result is not None:
        print "cached.."
        return HttpResponse(result)   
    
    jsonobj = simplejson.loads(jsonstr)
    lower_limit = 0
    upper_limit = 10
    if ('limits' in jsonobj):
        limits = jsonobj['limits'].partition('-')
        lower_limit = limits[0]
        upper_limit = limits[2]
        
    screener = None
    if ('screener' in jsonobj):
        screener = jsonobj['screener']
        
    sorter = None
    if ('sorter' in jsonobj):
        sorter = jsonobj['sorter']
    
    #cache_key = "%s-sorted-prods-%s-%s-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, screener, sorter, lower_limit, upper_limit)
    #cache_key = "amitaviv"
    #print cache_key 
    #result = cache.get(cache_key)
    #print result
    #if result is not None:
    #    print "cached.."
    #    return HttpResponse(result)   
     
    shop = lfs_get_object_or_404(Shop, pk=1)
    products = shop.get_ssp(screener,sorter,lower_limit,upper_limit)
    res = []
    for product in products:
        item = product.get_item()   
        if item == None: continue
        res.append({"image_url": product.get_item_image(), 
                    "name": product.name,
                    "price": product.price,
                    "material": item.material,
                    "text" : item.textParam,
                    "product_url": "/product/" + product.slug,
                    "slug" : product.slug,
                    "lovers" : product.stock_amount})
    result = simplejson.dumps({
        "products": res
    })
    cache.set(cache_key, result, 3600)
    #result = cache.get(cache_key)
    #print "wtf %s" % dd
    #return result
    return HttpResponse(result)  

def s3_signed_url(bucket_name, file_path):
    import boto
    s3conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3conn.get_bucket(bucket_name, validate=False)
    key = bucket.new_key(file_path)
    signed_url = key.generate_url(expires_in=300)
    #print signed_url
    return signed_url


def get_stl(request):
    print "get stl"
    slug = request.GET.get('product', '')#Product.objects.get()
    print slug
    product = Product.objects.get(slug=slug) #queryset[0].get_item()
    item = product.get_item()
    controller = Controller('near', 'Default', 1)
    print item.uuid
    controller.get_stl(item.uuid)
    url = "https://s3.amazonaws.com/deploy_stl_bucket/%s.stl" % item.uuid
    #signed_url = s3_signed_url("deploy_stl_bucket","%s.stl" % item.uuid)
    #print signed_url
    result = simplejson.dumps({
        "url": url
    }, cls=LazyEncoder)
    return HttpResponse(result)  

from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.utils import LazyEncoder
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
