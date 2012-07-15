import sys
import logging
import math
import time
import itertools
import base64
from datetime import datetime
from django.utils import simplejson
from suds.client import Client
from explorer.models import Item
import explorer.tasks
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from django.conf import settings
from django.contrib.sites.models import Site

class Renderer:
    """
    A client for the Rhino / Grasshopper web service
    """
    def __init__(self):
        self.site_name = Site.objects.get(id=settings.SITE_ID).name
        
        self.q_ready = self.site_name + '_ready'
        #self.q_request = site_name + '_request'
        
    def request_images_async(self, params):
        explorer.tasks.request_images.apply_async(args=[params], countdown=0)
        
    def request_images(self, params):
        scene = params[0]['scene']
        scene = scene.replace('.3dm','')
        q_name = "%s_%s_%s" % (self.site_name, scene, 'request')
        conn = SQSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        q = conn.create_queue(q_name)
        q.set_message_class(Message)
        params = self.trunc_params(params)
        messages = []
        for i in range(len(params)):
            #params[i]['params']['textParam'] = 'sunsun'
            body = simplejson.dumps(params[i])
            sys.stderr.write(body + "\n")
            messages.append((i,base64.b64encode(body),0))
           
        for j in range(int(math.ceil(float(len(params))/10.0))):
            conn.send_message_batch(q, messages[j*10:(j+1)*10])
        sys.stderr.write("\n\n\nSent messages\n\n\n")
        return
 
    def get_ready_images(self):
        conn = SQSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        q = conn.create_queue(self.q_ready)
        rs = q.get_messages(10)
        
        for i in range(len(rs)):
            sys.stderr.write(rs[i].get_body() + "\n")
            body = simplejson.loads(rs[i].get_body())
            if (body.has_key('status') == False):
                q.delete_message(rs[i])
                continue
            if(body['status']!='STARTED'):
                q.delete_message(rs[i])
                continue
            if (body['item_id'].find('_') != -1):
                continue
            item = Item.objects.get(uuid=body['item_id'])
            item.image_url = body['url']
            item.save()
            q.delete_message(rs[i])
            sys.stderr.write("\nRecieved results for "+str(body['item_id'])+"\n")                
            
            
    def trunc_params(self, params_list):
        nlist = [];
        for params in params_list:
            for k,v in params['params'].iteritems():
                if k == 'textParam':
                    continue
                nv = float("%.2f" % v)
                params['params'][k] = nv
            nlist.append(params)
        return nlist
                