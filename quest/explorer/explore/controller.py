import random
import sys
import time
import logging
from django.utils import simplejson
from datetime import datetime
#from explorer.explore.image_generator import Generator
from explorer.explore.renderer import Renderer
from explorer.models import Item, GhDefinition, ExplorerConfig
import explorer.tasks
from explorer.explore.algo import Axis, Explore, Iterate
from django.conf import settings
from django.contrib.sites.models import Site
import uuid


class Base:
    """
    Explore parameter space
    """
    def __init__(self, distance='medium', material='Default', page_size=None, explore_type='explore', textParam=''):
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
    
    
    def start_iterate(self, definition_id, param_index, text):
        logging.error(param_index)
        uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
        self.definition = GhDefinition.objects.get(pk=definition_id) 
        explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, None, self.page_size, self.distance, self.page_size, param_index, 'iterate', 'linear', self.definition.default_material.name, text], countdown=0)
        return self._make_result(uuids, [self.definition.default_material.name for i in range(self.page_size)])
    
    def explore(self, item_id, param_index, explore_type, iterate_type, text):
        #text = "ZOHAR"
        logging.error(item_id)
        self.root = Item.objects.get(uuid=item_id)
        self.param_index = int(param_index)
        self.definition = self.root.definition
        self.explore_type = explore_type
        self.iterate_type = iterate_type
        self.text = text
        if self.deep:
            return self._explore_deep()
        else:
            return self._explore()       
    
    def explore_product(self, item_id, param_index, explore_type, iterate_type):
        startItem = Item.objects.get(uuid=item_id)
        self.material = startItem.material
        self.text = startItem.textParam
        
        res = self.explore(item_id, param_index, explore_type, iterate_type, self.text)
        #res.append(self._prepare_result_item(self.root, len(res)))
        return res
    
    def item_to_product(self, item):
        jobs = []
        for view_name in ["Top","Front","Render"]:
            jobs.append(self._prepare_job(item.definition, item.uuid + '_' + view_name, item.params, item.textParam,view_name, item.material, 350)) 
        
        self.renderer.request_images_async(jobs) 
         
    def _explore(self):
        uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
        explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, self.root, self.page_size, self.distance, self.page_size, self.param_index, self.explore_type, self.iterate_type, self.material, self.text], countdown=0)
        self.root.selected=True
        self.root.save()
        return self._make_result(uuids, [self.material for i in range(self.page_size)])
        
    def render_materials(self, materials, parent_id, definition_id, text):
        if parent_id == None:
            root = None
            definition = GhDefinition.objects.get(pk=definition_id) 
        else:
            root = Item.objects.get(uuid=parent_id)
            definition = root.definition
            text = root.textParam
            
        self.iterate_type = 'linear'
        self.explore_type = 'iterate'
        
        uuids = map(lambda x: str(uuid.uuid1()), range(len(materials)))
       
        for i in range(len(materials)):
            explorer.tasks.send_jobs.apply_async(args=[definition, [uuids[i]], root, 1, self.distance, 1, -1, 'noop', self.iterate_type, materials[i], text], countdown=0)
        
        return self._make_result(uuids, materials)
    
    
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
    
    #def _get_children_params(self, explore_type, ):
                           
    def _send_jobs(self, definition, uuids, root, n_jobs, distance, param_index, explore_type, iterate_type, text):
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
           
        perm = random.sample(range(len(uuids)), n_jobs)
        jobs = []
        for p in perm:
            logging.warn(str(p))
            jobs.append(self._prepare_job(definition, uuids[p], children_params[p], text, "Render", self.material)) 
        self.renderer.request_images(jobs)  
        
        for i in range(len(uuids)):
            self._save_item(root, definition, children_params[i], (i in perm), uuids[i], distance, self.material, text)
    
    
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
        db_item = Item(price=price, selected=False, material = material, image_url=self._uuid_to_url(item_uuid), parent=parent, parent_distance=distance, definition=definition, sent=sent, uuid=item_uuid, params=params, textParam=textParam)
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