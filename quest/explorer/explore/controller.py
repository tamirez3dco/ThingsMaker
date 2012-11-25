import random
import math
import sys
import time
import logging
from django.utils import simplejson
from datetime import datetime
#from explorer.explore.image_generator import Generator
from explorer.explore.renderer import Renderer
from explorer.models import Item, GhDefinition, ExplorerConfig, DefinitionMaterial, DefinitionParam
import explorer.tasks
from django.conf import settings
from django.contrib.sites.models import Site
import uuid
import itertools

def all_perms(elements):
    if len(elements) <=1:
        yield elements
    else:
        for perm in all_perms(elements[1:]):
            for i in range(len(elements)):
                yield perm[:i] + elements[0:1] + perm[i:]

#[ [v1, v2, v3],  [v1, v2], ... ]
# bad memory usage, need to yield..
def all_params_perms(params):
    if len(params) <=1:
        return map(lambda x: [x], params[0])
    else:
        all_perms = []
        for v in params[0]:
            for perm in all_params_perms(params[1:]):
                np = [v] + perm
                all_perms.append(np)
        return all_perms
            
class Base:
    """
    Explore parameter space
    """
    def __init__(self, material='Default', explore_type='iterate', textParam=''):
        self.material = material
#        self.text = textParam
        self.text = "MUSSA"
       
        #self.deep_count=int(ExplorerConfig.objects.get(k__exact='deep_count').v)
        self.deep = False
        self.bake = "all"
        self.DEFAULT_VIEW = "Render"
        self.renderer = Renderer()

    def get_random_items(self, product):
        variants = product.get_random_variants(9)
        print len(variants)
        items = map(lambda x: x.get_item(), variants)
        return self._make_res_from_items(items)
    
    def _make_res_from_items(self, items):
        textParams = []
        materials = []
        all_uuids = []
        for i in range(len(items)):
            try:
                pp = str(items[i].textParam)
                textParams.append(pp)
            except:
                try:
                    pp = items[i].textParam
                    textParams.append(pp)
                except:
                    continue;
            materials.append(items[i].material)
            all_uuids.append(str(items[i].uuid))
     
        return self._make_result(all_uuids, materials, textParams, -1)

    def render_materials(self, parent_id, definition_id, text):
        if parent_id == None:
            root = None
            definition = GhDefinition.objects.get(pk=definition_id)
        else:
            root = Item.objects.get(uuid=parent_id)
            definition = root.definition
          
        if definition.accepts_text_params == False:
            text = ""    
            
        self.explore_type = 'iterate'
        materials = map(lambda x: x.material.name, DefinitionMaterial.objects.filter(definition=definition))
        
        (selected,params) = self._get_children_params(definition, root, -1, 'noop')
        print materials
        if root != None:
            selected = materials.index(root.material) 
            
        params = [params[0] for i in materials]
        #print params
        (all_uuids, todo_uuids, todo_params, todo_materials, todo_bases) = self._get_cached_items(definition, params, materials, text)
        #print (all_uuids, todo_uuids, todo_params, todo_materials, todo_bases) 
        for i in range(len(todo_materials)):
            base = None
            if len(todo_bases)>0:
                base = todo_bases[i]
            
            explorer.tasks.send_jobs.apply_async(kwargs={'base_models': [base]}, args=[definition, [todo_uuids[i]], None, [todo_params[i]], todo_materials[i], 'iterate', text])
     
        return self._make_result(all_uuids, materials, [text for i in range(len(all_uuids))], selected)
   
    def _explore(self):
        (selected,params) = self._get_children_params(self.definition, self.root, self.param_index, self.explore_type)
        materials = [self.material for i in range(len(params))]
        (all_uuids, todo_uuids, todo_params, todo_materials, todo_bases) = self._get_cached_items(self.definition, params, materials, self.text, param_index=self.param_index)
        explorer.tasks.send_jobs.apply_async(kwargs={'base_models': todo_bases, 'param_index': self.param_index}, args=[self.definition, todo_uuids, self.root, todo_params, self.material, 'iterate', self.text])
        print selected
        return self._make_result(all_uuids, materials, [self.text for i in range(len(all_uuids))], selected)
    
    
    def get_models(self, definition, parent, param_index):
        params = self._get_children_params(self.definition, self.root, self.param_index, self.explore_type)
    
    def _get_cached_items(self, definition, params, materials, text, param_index=None):
        #self._get_base_cache(definition, params)
        all_uuids = []
        todo_uuids = []
        todo_params = []
        todo_materials = []
        todo_bases = []
        cache_count = 0
        view = self._get_view(definition, param_index)
        if view == self.DEFAULT_VIEW:
            view = ""
            
        for p,m in zip(params, materials):
            #param_key = self._item_param_hash(p, "", "","")
            param_key = self._item_param_hash(p, m, text,view)
            cached = Item.objects.filter(param_hash = param_key, definition = definition)
            
            if len(cached)>0 and (definition.use_cache==True):
                cache_count += 1
                if (cached[0].status == Item.ERROR):
                    continue
                if (cached[0].status == Item.CREATED):
                    todo_uuids.append(cached[0].uuid)
                    todo_materials.append(m)
                    todo_params.append(p)
                
                all_uuids.append(cached[0].uuid) 
                
            else:
                if (definition.base_definition!=None):
                    #print definition.base_definition.id
                    param_key = self._item_param_hash(p, "", "","")
                    #print param_key
                    cached_base = Item.objects.filter(base_param_hash = param_key, definition = definition.base_definition)
                    if len(cached_base)>0:
                        if(cached_base[0].status == Item.ERROR): continue
                        todo_bases.append(cached_base[0].uuid)
                        
                new_uuid = str(uuid.uuid1())
                todo_uuids.append(new_uuid)
                todo_materials.append(m)
                todo_params.append(p)
                all_uuids.append(new_uuid)
               
        logging.error("all %s, todo %s, cached %s" % (len(materials), len(todo_uuids), cache_count))
        return (all_uuids, todo_uuids, todo_params, todo_materials, todo_bases) 
    
    def _get_base_cache(self, definition, params):
        param_key = self._item_param_hash(params, "", "", "")
        cached = Item.objects.filter(base_param_hash = param_key, definition = definition)
            
        return cached[0].uuid
            
    def _item_param_hash(self, params, material, text, view):
        #hacked_params = filter(lambda x: x.)
        p = "".join(map(lambda x: ("%.2f" %  x)[0:], params)) + material + text + view
        return p
        
        
        #comment
        
    def explore(self, item_id, param_index, explore_type, text):
        self.root = Item.objects.get(uuid=item_id)
        self.param_index = int(param_index)
        self.definition = self.root.definition
        self.explore_type = explore_type
        
        if self.definition.accepts_text_params == False:
            text = ""
        
        self.text = text
        if self.deep:
            return self._explore_deep()
        else:
            return self._explore()       
    
    def item_to_product(self, item):
        base = None
        if item.definition.base_definition != None:
            base = self._get_base_cache(item.definition.base_definition, item.params) 
            
        job = self._prepare_job(item.definition, item.uuid + '_' + 'Render', item.params, item.textParam,'Render', item.material, 350, base_model=base)
        self.renderer.request_images_async([job]) 
        
        jobs = []
        for view_name in ["Top","Front"]:
            jobs.append(self._prepare_job(item.definition, item.uuid + '_' + view_name, item.params, item.textParam,view_name, item.material, 350, base_model=base)) 
            
        self.renderer.request_images_async(jobs, countdown=1) 
        
        job = self._prepare_job(item.definition, item.uuid, item.params, item.textParam,'Render', item.material, 180, base_model=base)
        self.renderer.request_images_async([job]) 
    
    def get_stl(self, item_id):
        item = Item.objects.get(uuid=item_id)
        job = self._prepare_job(item.definition, item.uuid+ '-sw', item.params, item.textParam,"Render", item.material, 674, True)
        self.renderer.request_images_async([job]) 
    
    def _get_children_params(self, definition, root, param_index, explore_type ):
        if explore_type=='noop' and root!=None:
            children_params = [root.params]
            selected=-1
        else:
            (selected, children_params) = self._get_page_params(definition, root, param_index)
        
        return (selected,children_params)    
   
    def _get_page_params(self, definition, root, param_index):
        if root!=None:
            parent_params = root.params
        else:
            parent_params = self._get_initial_page_params(definition)
        
        if param_index < 0:
            return (-1,[parent_params])
        
        db_param = DefinitionParam.objects.get(definition=definition,index=param_index)
        param_values = db_param.get_values()
        params_list = []
        selected=-1
        for i in range(len(param_values)):
            param = param_values[i]
            params = list(parent_params)
            if params[param_index] == param:
                selected=i
            params[param_index] = param
            params_list.append(params)
        
        #print params_list
        return (selected,params_list)
    
    def _get_initial_page_params(self, definition):
        db_params = DefinitionParam.objects.filter(definition=definition, active=True).order_by('index')
        return map(lambda x: x.get_initial_value(), db_params)

    def _get_view(self, definition, param_index):
        view = self.DEFAULT_VIEW
        if (param_index!=None):
            db_param = DefinitionParam.objects.get(definition=definition,index=param_index)
            if db_param.rendering_view != None:
                view = db_param.rendering_view
        return view
                
    def _send_jobs(self, definition, uuids, root, children_params, text, base_models=None, low_priority=False, get_stl=False, param_index=None):
        jobs = []
        base_model=None
        view = self._get_view(definition, param_index)
        for i in range(len(uuids)):
            if(base_models!=None)and(len(base_models)>0):
                base_model = base_models[i]
            jobs.append(self._prepare_job(definition, uuids[i], children_params[i], text, view, self.material, low_priority=low_priority, get_stl=get_stl, base_model=base_model))
        
        self.renderer.request_images(jobs)  
        
        for i in range(len(uuids)):
            saved = Item.objects.filter(uuid=uuids[i])
            if(len(saved)==0):
                self._save_item(root, definition, children_params[i], True, uuids[i], self.material, text, view=view)
            else:
                saved[0].sent = True
                saved[0].status = Item.SENT
                saved[0].save()
        
    def _uuid_to_url(self, item_uuid):
        return "http://s3.amazonaws.com/%s_Bucket/%s.jpg" % (Site.objects.get(id=settings.SITE_ID).name, item_uuid) 
    
    def _prepare_job(self, definition, item_id, params, text, view_name, material, width=180, get_stl=False, low_priority=False, base_model=None):
        job = {}
        
        job['params'] = dict(zip(definition.param_names(), params))
        if (definition.accepts_text_params):
            textToSend = "test"
            if (text != None):
                textToSend = text
            job['params']['textParam'] = textToSend
        job['item_id'] = item_id
        job['bake'] = self.bake
        job['operation'] = 'render_model'
        job['width'] = width
        job['height'] = width
        job['gh_file'] = definition.file_name
        job['scene'] = definition.scene_file 
        job['layer_name'] = material
        job['view_name'] = view_name
        job['getSTL'] = get_stl
        job['low_priority'] = low_priority
        if base_model!=None:
            job['load_stl'] = base_model
            
        return job
    
    def _make_result(self, uuids, materials, textParams, selected):
        def do(x):
            return  { "id": x[0], "image_url": self._uuid_to_url(x[0]), "price": 172, "index": x[1], "material": x[2], "text": x[3]}
        return {'selected': selected, 'items': map(do, zip(uuids, range(len(uuids)), materials, textParams))}
        
    def _prepare_result_item(self, item, index):
        return  { "id": str(item.uuid), "image_url": item.image_url, "price": float(item.price), "index": index}

    def _save_item(self, parent, definition, params, sent, item_uuid, material, textParam, view=""):
        price = 172       
        if view == self.DEFAULT_VIEW:
            view = ""
        
        param_hash = self._item_param_hash(params, material, textParam, view)
        base_param_hash = self._item_param_hash(params, "", "", "")
        if (sent == True):
            status = Item.SENT
        else:
            status = Item.CREATED
        
        old_items = Item.objects.filter(uuid=item_uuid)
        if len(old_items)!=0:
            old_items[0].status = status
            old_items[0].save()
            return old_items[0]
            
        db_item = Item(base_param_hash=base_param_hash,param_hash=param_hash, price=price, selected=False, material = material, image_url=self._uuid_to_url(item_uuid), parent=parent, definition=definition, sent=sent, status=status,uuid=item_uuid, params=params, textParam=textParam)
        db_item.save()
        #db_item.set_params(params)
        return db_item
    
    def _copy_item(self, obj):
        from copy import deepcopy
        old_obj = deepcopy(obj)
        old_obj.id = None
        old_obj.selected = False
        old_obj.parent = None
        old_obj.uuid = str(uuid.uuid1())
        old_obj.save()
        return old_obj
   
    def send_background_items(self, definition=None):
        max_wait = 100
        
        if definition!=None:
            not_sent = Item.objects.filter(sent=False, definition=definition)
        else: 
            not_sent = Item.objects.filter(sent=False)
      
        wait_count = self.renderer.get_lowpriority_wait_count(['vases','rings','cases','pendants'])
        can_send = max_wait - wait_count
       
        print "Not Sent: %s, Can Send: %s" % (not_sent.count(), can_send) 
        for i in range(min(can_send,not_sent.count())):
            print not_sent[i].uuid
            self.material = not_sent[i].material
            self._send_jobs(not_sent[i].definition, [not_sent[i].uuid], None, [not_sent[i].params], 0, "", get_stl=True, low_priority=True)
            
    def preprocess_definition(self, definition):
        db_params = DefinitionParam.objects.filter(definition=definition, active=True).order_by('index')
        param_values = map(lambda x: x.get_values(), db_params)
        print param_values
        param_perms = all_params_perms(param_values)
        #if (definition)##
        #materials = map(lambda x: x.material.name, DefinitionMaterial.objects.filter(definition=definition))
        materials = [definition.default_material.name]
        print materials
        for material in materials:
            print material
            #param_perms = itertools.product(param_values, repeat=len(param_names))
            #print param_perms
            for perm in param_perms:
                print perm
                item_uuid = str(uuid.uuid1())
                self._save_item(None, definition, perm, False , item_uuid, material, "")
 
    def process_ghx(self, definition):
        self.renderer.adjust_ghx(definition.current_file_name)
 
#    def _explore_deep(self):
#        children = None
#        for i in range(100):
#            children = Item.objects.filter(parent__exact=self.root.id, parent_distance=self.distance)
#            if children.count() >= self.page_size:
#                break
#            else:
#                logging.warn('sleeping')
#                time.sleep(0.1)
#                
#        explorer.tasks.send_missing_jobs.apply_async(args=[children], countdown=0)
#        explorer.tasks.send_deep_jobs.apply_async(args=[children], countdown=1)
#        
#        self.root.selected=True
#        self.root.save()
#        
#        uuids = map(lambda x: x.uuid, children)
#        return self._make_result(uuids, [self.material for i in range(self.page_size)])
#    
#    def _send_missing_jobs(self, items):
#        jobs=[]
#        for item in items:
#            if item.sent != True:
#                item.sent=True
#                item.save()
#                logging.warn(item.uuid + 'missing!!!!')
#                jobs.append(self._prepare_job(item.definition, item.uuid, item.params, item.textParam, "Render", item.material)) 
#        self.renderer.request_images(jobs)          
#        
#    def _send_deep_jobs(self, items):
#        for item in items:
#            for distance in self.distances.keys():
#                uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
#                self._send_jobs(item.definition, uuids, item, self.deep_count, distance)
#   
#class Remember(Base):
#    def stam(self):
#        pass