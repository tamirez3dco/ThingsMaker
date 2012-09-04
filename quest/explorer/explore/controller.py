import random
import sys
import time
import logging
from django.utils import simplejson
from datetime import datetime
#from explorer.explore.image_generator import Generator
from explorer.explore.renderer import Renderer
from explorer.models import Item, GhDefinition, ExplorerConfig, DefinitionMaterial
import explorer.tasks
from explorer.explore.algo import Axis, Explore, Iterate
from django.conf import settings
from django.contrib.sites.models import Site
import uuid


class Base:
    """
    Explore parameter space
    """
    def __init__(self, distance='medium', material='Default', page_size=None, explore_type='iterate', textParam=''):
        self.distance = distance
        self.material = material
        self.text = textParam
        if page_size==None:
            self.page_size = int(ExplorerConfig.objects.get(k__exact='page_size').v)
        else:
            self.page_size = page_size
            
        self.row_size = int(ExplorerConfig.objects.get(k__exact='row_size').v)
        self.deep_count=int(ExplorerConfig.objects.get(k__exact='deep_count').v)
        self.deep = False
        self.bake = "all"
        self.renderer = Renderer()
        self.distances = {
            'near': [0.01, 0.09],
            'medium': [0.05, 0.2]
        };
        if explore_type == 'explore':
            self.algo = Explore(self.page_size, self.row_size)
        if explore_type == 'axis':
            self.algo = Axis(self.page_size, self.row_size)
        if explore_type == 'iterate' or explore_type == 'noop':
            self.algo = Iterate(self.page_size, self.row_size)
        
#    def get_definitions(self):
#        defs = GhDefinition.objects.all()  
#        items = []  
#        for d in defs:
#            if d.active == False:
#                continue
#            url = 'https://s3.amazonaws.com/amit_Bucket/34623.jpg'
#            if d.image:
#                url = 'data:image/jpg;base64,' + d.image
#            item = { "id": str(d.id), "image_url": url, "price": 172.00 }
#            items.append(item)
#        return items  
    
    def get_definitions(self):
        defs = GhDefinition.objects.all()  
        items = []  
        for d in defs:
            if d.active != True:
                continue
            self.definition = d
            c = Item.objects.filter(image_url__isnull=False, definition=d).count()
            item = None
            if (c<10):
                self.page_size = 60
                self.algo.page_size = self.page_size
                uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
                explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, None, self.page_size, self.distance, self.page_size, 0, 'explore', 'linear', 'Default', 'naama'], countdown=0)
            else: 
                rep = None
                r = Item.objects.filter(image_url__isnull=False, selected=True, definition=d).count()
                if r>0: 
                    rep = Item.objects.filter(image_url__isnull=False, selected=True, definition=d).order_by('?')[0]  
                else:
                    rep = Item.objects.filter(image_url__isnull=False, sent=True, definition=d).order_by('?')[0]  
                item = { "id": str(d.id), "image_url": rep.image_url, "price": 172.00 }                 
            items.append(item)
            
        return items  
    
    def create_param_reps(self):
        pass
    
    def start_exploration(self, definition_id): 
        #self.page_size = self.page_size+1;
        self.definition = GhDefinition.objects.get(pk=definition_id) 

        r = Item.objects.filter(image_url__isnull=False, selected=True, definition=self.definition).count()
        reps=[]
        if r>10: 
            reps = Item.objects.filter(image_url__isnull=False, selected=True, definition=self.definition).order_by('?')[:self.page_size]  
        else:
            reps = Item.objects.filter(image_url__isnull=False, sent=True, definition=self.definition).order_by('?')[:self.page_size]  
        copies = map(lambda x: self._copy_item(x), reps)
        if(self.deep):
            explorer.tasks.send_deep_jobs.apply_async(args=[copies], countdown=0)
        items = map(lambda x: self._prepare_result_item(x[0], x[1]), zip(copies, range(len(copies))))
        return items
    
    def get_random_items(self, product):
        variants = product.get_random_variants(6)
        print len(variants)
        items = map(lambda x: x.get_item(), variants)
        result = map(lambda x: self._prepare_result_item(x[0], x[1]), zip(items, range(len(items))))
        return result
    
    def start_iterate(self, definition_id, param_index, text):
        #logging.error(param_index)
        self.algo = Iterate(self.page_size, self.row_size)
        #uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
        self.definition = GhDefinition.objects.get(pk=definition_id) 
       
        params = self._get_children_params(self.definition, None, self.distance, param_index, 'iterate', 'linear')
        materials = [self.definition.default_material.name for i in range(len(params))]
        if self.definition.accepts_text_params == False:
            text = ""
        (all_uuids, todo_uuids, todo_params, todo_materials) = self._get_cached_items(self.definition, params, materials, text)
       
        #explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, None, self.page_size, self.distance, self.page_size, param_index, 'iterate', 'linear', self.definition.default_material.name, text], countdown=0)
        explorer.tasks.send_jobs_with_params.apply_async(args=[self.definition, todo_uuids, None, todo_params, self.distance, self.definition.default_material.name, self.page_size, 'iterate', text])
        return self._make_result(all_uuids, materials)
    
    def _get_cached_items(self, definition, params, materials, text):
        all_uuids = []
        todo_uuids = []
        todo_params = []
        todo_materials = []
        for p,m in zip(params, materials):
            param_key = self._item_param_hash(p, m, text)
            #logging.error(param_key)
            cached = Item.objects.filter(param_hash = param_key, definition = definition)
            #res = []
            if len(cached)>0:
                all_uuids.append(cached[0].uuid)
                #logging.error("found %s %s" % (param_key, cached[0].uuid))
            else:
                new_uuid = str(uuid.uuid1())
                todo_uuids.append(new_uuid)
                todo_materials.append(m)
                todo_params.append(p)
                all_uuids.append(new_uuid)
                
        logging.error("all %s, todo %s" % (len(materials), len(todo_uuids)))
        return (all_uuids, todo_uuids, todo_params, todo_materials) 
    
    def _item_param_hash(self, params, material, text):
        p = "".join(map(lambda x: ("%.2f" %  x)[2:], params)) + material + text
        return p
        
    def explore(self, item_id, param_index, explore_type, iterate_type, text):
        self.root = Item.objects.get(uuid=item_id)
        self.param_index = int(param_index)
        self.definition = self.root.definition
        self.explore_type = explore_type
        self.iterate_type = iterate_type
        if self.definition.accepts_text_params == False:
            text = ""
        
        self.text = text
        if self.deep:
            return self._explore_deep()
        else:
            return self._explore()       
    
    def item_to_product(self, item):
        jobs = []
        for view_name in ["Render"]:
            jobs.append(self._prepare_job(item.definition, item.uuid + '_' + view_name, item.params, item.textParam,view_name, item.material, 350)) 
     
        self.renderer.request_images_async(jobs) 
        
        jobs = []
        for view_name in ["Top","Front"]:
            jobs.append(self._prepare_job(item.definition, item.uuid + '_' + view_name, item.params, item.textParam,view_name, item.material, 350)) 
            
        self.renderer.request_images_async(jobs, countdown=1) 
         
    def _explore(self):
        #uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
        params = self._get_children_params(self.definition, self.root, self.distance, self.param_index, self.explore_type, self.iterate_type)
        materials = [self.material for i in range(len(params))]
        (all_uuids, todo_uuids, todo_params, todo_materials) = self._get_cached_items(self.definition, params, materials, self.text)
        #explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, self.root, self.page_size, self.distance, self.page_size, self.param_index, self.explore_type, self.iterate_type, self.material, self.text], countdown=0)
        explorer.tasks.send_jobs_with_params.apply_async(args=[self.definition, todo_uuids, self.root, todo_params, self.distance, self.material, self.page_size, 'iterate', self.text])
        
        self.root.selected=True
        self.root.save()
        return self._make_result(all_uuids, materials)
        
    def render_materials(self, materials, parent_id, definition_id, text):
        if parent_id == None:
            root = None
            definition = GhDefinition.objects.get(pk=definition_id)
        else:
            root = Item.objects.get(uuid=parent_id)
            definition = root.definition
            if text == "":
                text = root.textParam
            
        if definition.accepts_text_params == False:
            text = ""    
            
        self.iterate_type = 'linear'
        self.explore_type = 'iterate'
        materials = map(lambda x: x.material.name, DefinitionMaterial.objects.filter(definition=definition))
        
        #uuids = map(lambda x: str(uuid.uuid1()), range(len(materials)))
       
        params = self._get_children_params(definition, root, self.distance, -1, 'noop', 'linear') 
        params = [params[0] for i in materials]
        (all_uuids, todo_uuids, todo_params, todo_materials) = self._get_cached_items(definition, params, materials, text)
        for i in range(len(todo_materials)):
            explorer.tasks.send_jobs_with_params.apply_async(args=[definition, [todo_uuids[i]], None, [todo_params[i]], self.distance, todo_materials[i], self.page_size, 'iterate', text])
       
       
        #for i in range(len(materials)):
        #    explorer.tasks.send_jobs.apply_async(args=[definition, [uuids[i]], root, 1, self.distance, 1, -1, 'noop', self.iterate_type, materials[i], text], countdown=0)
        
        return self._make_result(all_uuids, materials)
    
    
    def _explore_deep(self):
        children = None
        for i in range(100):
            children = Item.objects.filter(parent__exact=self.root.id, parent_distance=self.distance)
            if children.count() >= self.page_size:
                break
            else:
                logging.warn('sleeping')
                time.sleep(0.1)
                
        explorer.tasks.send_missing_jobs.apply_async(args=[children], countdown=0)
        explorer.tasks.send_deep_jobs.apply_async(args=[children], countdown=1)
        
        self.root.selected=True
        self.root.save()
        
        uuids = map(lambda x: x.uuid, children)
        return self._make_result(uuids, [self.material for i in range(self.page_size)])
    
    def _send_missing_jobs(self, items):
        jobs=[]
        for item in items:
            if item.sent != True:
                item.sent=True
                item.save()
                logging.warn(item.uuid + 'missing!!!!')
                jobs.append(self._prepare_job(item.definition, item.uuid, item.params, item.textParam, "Render", item.material)) 
        self.renderer.request_images(jobs)          
        
    def _send_deep_jobs(self, items):
        for item in items:
            for distance in self.distances.keys():
                uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
                self._send_jobs(item.definition, uuids, item, self.deep_count, distance)
    
    def _get_children_params(self, definition, root, distance, param_index, explore_type, iterate_type ):
        children_params = None
        if explore_type == 'noop':
            if root==None:
                children_params = self.algo.get_initial_page_params(len(definition.param_names), param_index)
            else:
                children_params = [root.params]
        else:
            if root==None:
                if explore_type=='iterate':
                    children_params = self.algo.get_initial_page_params(len(definition.param_names), param_index)
                else:
                    children_params = self.algo.get_random_page_params(len(definition.param_names))
            
            else:
                children_params = self.algo.get_page_params(root.params, self.distances[distance], param_index, iterate_type)
           
        return children_params     
    #def _get
                      
    def _send_jobs(self, definition, uuids, root, n_jobs, distance, param_index, explore_type, iterate_type, text):
        children_params = self._get_children_params(definition, root, distance, param_index, explore_type, iterate_type)
        perm = random.sample(range(len(uuids)), n_jobs)
        jobs = []
        for p in perm:
            #logging.warn(str(p))
            jobs.append(self._prepare_job(definition, uuids[p], children_params[p], text, "Render", self.material)) 
        self.renderer.request_images(jobs)  
        
        for i in range(len(uuids)):
            self._save_item(root, definition, children_params[i], (i in perm), uuids[i], distance, self.material, text)
    
    
    def _send_jobs_with_params(self, definition, uuids, root, children_params, distance, text):
        jobs = []
        for i in range(len(uuids)):
            jobs.append(self._prepare_job(definition, uuids[i], children_params[i], text, "Render", self.material))
        
        self.renderer.request_images(jobs)  
        
        for i in range(len(uuids)):
            self._save_item(root, definition, children_params[i], True, uuids[i], distance, self.material, text)
        
    def _uuid_to_url(self, item_uuid):
        return "http://s3.amazonaws.com/%s_Bucket/%s.jpg" % (Site.objects.get(id=settings.SITE_ID).name, item_uuid) 
    
    def _prepare_job(self, definition, item_id, params, text, view_name, material, width=180):
        job = {}
        job['params'] = dict(zip(definition.param_names, params))
        if (definition.accepts_text_params):
            textToSend = "test"
            if (text != None):
                textToSend = text
            job['params']['textParam'] = textToSend
        job['item_id'] = item_id #+ '_' + str(width)
        job['bake'] = self.bake
        job['operation'] = 'render_model'
        job['width'] = width
        job['height'] = width
        job['gh_file'] = definition.file_name
        job['scene'] = definition.scene_file 
        job['layer_name'] = material
        job['view_name'] = view_name
        return job
    
    def _make_result(self, uuids, materials):
        def do(x):
            return  { "id": x[0], "image_url": self._uuid_to_url(x[0]), "price": 172, "index": x[1], "material": x[2]}
        return map(do, zip(uuids, range(len(uuids)), materials))
        
    def _prepare_result_item(self, item, index):
        return  { "id": str(item.uuid), "image_url": item.image_url, "price": float(item.price), "index": index}

    def _save_item(self, parent, definition, params, sent, item_uuid, distance, material, textParam):
        price = 172
        
        param_hash = self._item_param_hash(params, material, textParam)
        db_item = Item(param_hash=param_hash, price=price, selected=False, material = material, image_url=self._uuid_to_url(item_uuid), parent=parent, parent_distance=distance, definition=definition, sent=sent, uuid=item_uuid, params=params, textParam=textParam)
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
    

class Remember(Base):
    def stam(self):
        pass