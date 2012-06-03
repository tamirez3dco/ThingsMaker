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
from explorer.explore.algo import Directions as Algo
from django.conf import settings
from django.contrib.sites.models import Site
import uuid


class Controller:
    """
    Explore parameter space
    """
    def __init__(self, distance='medium', page_size=None):
        self.distance = distance
        if page_size==None:
            self.page_size = int(ExplorerConfig.objects.get(k__exact='page_size').v)
        else:
            self.page_size = page_size
            
        self.row_size = int(ExplorerConfig.objects.get(k__exact='row_size').v)
        self.deep_count=int(ExplorerConfig.objects.get(k__exact='deep_count').v)
        self.deep = True
        self.bake = "all"
        self.renderer = Renderer()
        self.distances = {
            'near': [0.01, 0.13],
            'medium': [0.05, 0.25]
        };
        self.algo = Algo(self.page_size, self.row_size)
        
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
                explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, None, self.page_size, self.distance, self.page_size], countdown=0)
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
        self.page_size = self.page_size+1;
        self.definition = GhDefinition.objects.get(pk=definition_id) 
        #children_params = self.algo.get_random_page_params(len(self.definition.param_names))
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
        
    def explore(self, item_id):
        self.root = Item.objects.get(uuid=item_id)
        self.definition = self.root.definition
        if self.deep:
            return self._explore_deep()
        else:
            return self._explore()       
     
    def _explore(self):
        uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
        explorer.tasks.send_jobs.apply_async(args=[self.definition, uuids, self.root, self.page_size, self.distance, self.page_size], countdown=0)
        self.root.selected=True
        self.root.save()
        return self._make_result(uuids)
        
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
        return self._make_result(uuids)
    
    def _send_missing_jobs(self, items):
        jobs=[]
        for item in items:
            if item.sent != True:
                item.sent=True
                item.save()
                logging.warn(item.uuid + 'missing!!!!')
                jobs.append(self._prepare_job(item.definition, item.uuid, item.params)) 
        self.renderer.request_images(jobs)          
        
    def _send_deep_jobs(self, items):
        for item in items:
            for distance in self.distances.keys():
                uuids = map(lambda x: str(uuid.uuid1()), range(self.page_size))
                self._send_jobs(item.definition, uuids, item, self.deep_count, distance)
                       
    def _send_jobs(self, definition, uuids, root, n_jobs, distance):
        children_params = None
        if root==None:
            children_params = self.algo.get_random_page_params(len(definition.param_names))
        else:
            children_params = self.algo.get_page_params(root.params, self.distances[distance])
       
        perm = random.sample(range(len(uuids)), n_jobs)
        jobs = []
        for p in perm:
            logging.warn(str(p))
            jobs.append(self._prepare_job(definition, uuids[p], children_params[p])) 
        self.renderer.request_images(jobs)  
        
        for i in range(len(uuids)):
            self._save_item(root, definition, children_params[i], (i in perm), uuids[i], distance)
        
    def _uuid_to_url(self, item_uuid):
        return "http://s3.amazonaws.com/%s_Bucket/%s.jpg" % (Site.objects.get(id=settings.SITE_ID).name, item_uuid) 
    
    def _prepare_job(self, definition, item_id, params):
        job = {}
        job['params'] = dict(zip(definition.param_names, params))
        job['item_id'] = item_id
        job['bake'] = self.bake
        job['operation'] = 'render_model'
        job['gh_file'] = definition.file_name
        job['scene'] = definition.scene_file 
        return job
    
    def _make_result(self, uuids):
        def do(x):
            return  { "id": x[0], "image_url": self._uuid_to_url(x[0]), "price": 172, "index": x[1]}
        return map(do, zip(uuids, range(len(uuids))))
        
    def _prepare_result_item(self, item, index):
        return  { "id": str(item.uuid), "image_url": item.image_url, "price": float(item.price), "index": index}

    def _save_item(self, parent, definition, params, sent, item_uuid, distance):
        price = 172
        db_item = Item(price=price, selected=False, image_url=self._uuid_to_url(item_uuid), parent=parent, parent_distance=distance, definition=definition, sent=sent, uuid=item_uuid, params=params)
        db_item.save()
       # db_item.set_params(params)
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
