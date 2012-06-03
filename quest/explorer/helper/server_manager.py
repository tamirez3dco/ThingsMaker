import sys
import math
from boto.ec2.connection import EC2Connection
from django.utils import simplejson
from explorer.models import Item, ExplorerConfig, AppData
from django.db.models import Max
from datetime import timedelta, datetime
from django.conf import settings
from django.contrib.sites.models import Site
import logging

class ServerManager:
    """
    Managing server pool
    """
    def __init__(self):
        instance_types = {'amit': 'm2.2xlarge', 'tamir': 't1.micro', 'deploy': 'm2.2xlarge'}
        
        site_name = Site.objects.get(id=settings.SITE_ID).name
       
        self.security_groups = ['tamir_security_group_1']
        self.instance_type = instance_types[site_name]
        #self.image_id = "ami-ee69ce87"
        self.tag = site_name + '_auto'
        
        self.allow_idle = 600
        self.allow_idle_after_wakeup = 1000
            
    def manage(self):
        last_wakeup = AppData.objects.get(name__exact='main').last_wakeup
        last_item_created = Item.objects.all().aggregate(Max('created'))
        d1 = (datetime.now() - last_item_created['created__max'])
        d2 = (datetime.now() - last_wakeup)
        sys.stderr.write("\n\n"+str(d1.seconds)+" "+str(d2.seconds)+"\n\n")
        if (d1.seconds < self.allow_idle):
            self.wake_up(False)
        
    
    def wake_up(self, manual):
        if manual:
            data = AppData.objects.get(name__exact='main')
            data.last_wakeup = datetime.now()
            data.save()
            return
            
        c = self.find_needed_server_count()
        r = self.get_running()
        
        if c > len(r):
            self.launch(c-len(r))
            return
        
        if c < len(r):
            self.terminate(len(r)-c)   
            
    def get_all_running(self):
        conn = EC2Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        reservations = conn.get_all_instances()
        running = []
        for r in reservations:
            for inst in r.instances:
                if ((inst.state_code==16)or(inst.state_code==0)):
                    running.append(inst)
        return running
            
    def get_running(self):
        conn = EC2Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        reservations = conn.get_all_instances()
        running = []
        for r in reservations:
            for inst in r.instances:
                if (self.tag in inst.tags) and ((inst.state_code==16)or(inst.state_code==0)):
                    running.append(inst)
        return running
    
    #count == 0 -> terminate all
    def terminate(self, count):
        running = self.get_running()
        
        if (count==0):
            count = len(running)
            
        for i in range(count):
            running[i].terminate()
            
    def launch(self, count):
        conn = EC2Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        site_name = Site.objects.get(id=settings.SITE_ID).name
        userDataObj = {}
        userDataObj["num_of_rhino_instances"]=2
        userDataObj["visible_rhino"]=False
        userDataObj["scene"]="scene15.3dm"
        userDataObj["request_Q_name"]=site_name+"_request"
        userDataObj["ready_Q_name"]=site_name+"_ready"
        userDataObj["s3_bucketName"]=site_name+"_Bucket"
        userDataObj["idle_minutes_to_shutdown"]=30
        userDataObj["is_amazon_machine"]=True
        userDataString = simplejson.dumps(userDataObj)
        print ("userDataString(before lauch)=" + userDataString)
        my_image_id = ExplorerConfig.objects.get(k__exact='rhino_server_AMI').v
        print "my_image_id=" + my_image_id
        r = conn.run_instances(image_id=my_image_id,
                               instance_type=self.instance_type, 
                               security_groups=self.security_groups, 
                               min_count=1, 
                               max_count=count,
                               user_data=userDataString)
        all_running = self.get_all_running()
        for inst in r.instances:
            print "Tamir:inst=" + str(inst)
            for runer in all_running:
                print "Tamir:runer=" + str(runer)
        for inst in r.instances:
            inst.add_tag(self.tag)
            inst.add_tag('Name', self.tag)
    
    def find_needed_server_count(self):
        return int(ExplorerConfig.objects.get(k__exact='number_of_servers').v)
        page_size = int(ExplorerConfig.objects.get(k__exact='page_size').v)
        deep_count = int(ExplorerConfig.objects.get(k__exact='deep_count').v)
        images_per_server = float(ExplorerConfig.objects.get(k__exact='images_per_server').v)
        #logging.warning(str(needed))
        images_per_click = (page_size * deep_count) + (page_size-deep_count)
            
        needed = int(math.ceil(float(images_per_click)/float(images_per_server)))
        logging.warning(str(needed))
        return needed
        
        
        
