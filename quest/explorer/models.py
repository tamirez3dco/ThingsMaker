import math
import uuid
from django.db import models
#import cPickle as pickle
from django.utils import simplejson as pickle
from django.conf import settings
from south.modelsinspector import add_introspection_rules
import boto
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat
#from lfs.catalog.models import Product
#from lfs.catalog.models import Product

def file_name_suffix(name):
    l = name.split('.')
    return l[len(l)-1]

def get_gh_upload_path(instance, filename=None): 
    suffix = file_name_suffix(filename) 
    instance.current_file_name = "%s.%s" % (str(uuid.uuid1()), suffix)
    instance.file_name = "%s_adj.%s" % (str(uuid.uuid1()), suffix)
    instance.uploaded_file_name = filename
    return "%s/%s" % ( 
            'gh_files', 
            instance.current_file_name,
            ) 

class PickledObject(str):
    """A subclass of string so it can be told whether a string is
       a pickled object or not (if the object is an instance of this class
       then it must [well, should] be a pickled one)."""
    pass

class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in de-pickling
            # it should be allowed to propogate.
            return pickle.loads(str(value))
        else:
            try:
                return pickle.loads(str(value))
            except:
                # If an error was raised, just return the plain value
                return value
    
    def get_db_prep_save(self, value):
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value
    
    def get_internal_type(self): 
        return 'TextField'
    
    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value)
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v) for v in value]
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)

add_introspection_rules([], ["^explorer\.models\.PickledObjectField"])
class Material(models.Model):
    name = models.CharField(max_length=100)
    readable_name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

def get_material():
    m = Material.objects.all()[0]
    print m
    return Material.objects.all()[0]

class GhDefinition(models.Model):
    ADJUSTED_SUFFIX = '_adj'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    file_name = models.CharField(max_length=100, null=True)
    uploaded_file = models.FileField(upload_to=get_gh_upload_path, null=True) 
    current_file_name = models.CharField(max_length=100, null=True)
    uploaded_file_name = models.CharField(max_length=100, null=True)
    active = models.BooleanField()
    scene_file = models.CharField(max_length=100, blank=True)
    #product = models.IntegerField()
    accepts_text_params = models.BooleanField(default=False,blank=True)
    default_material = models.ForeignKey(Material, default=get_material, null=True, blank=True)
    use_cache = models.BooleanField(default=True, blank=True)
    base_definition = models.ForeignKey('self', null=True, db_index=True, default=None, blank=True)
    material_title = models.CharField(max_length=20, default='Material')
    
    @staticmethod
    def parse_message(message):
        definitions = GhDefinition.objects.filter(current_file_name=message['gh_file'])
        if (len(definitions)==0):
            return False
        definition =  definitions[0]
        Item.objects.filter(definition=definition).delete()

        old_params = DefinitionParam.objects.filter(definition=definition)
        sliders = message['sliders']
        sliders_dict={}
        for param in sliders:
            sliders_dict[param['new_name']]=param

        for older in old_params:
            if (not older.name in sliders_dict):
                older.delete()    
        
        older_params = DefinitionParam.objects.filter(definition=definition).order_by('order')
        order=0
        for older in older_params:
            older.order = order
            order = order + 1
            older.save()

        for param in message['sliders']:
            old_param = DefinitionParam.objects.filter(definition=definition, name=param['new_name'])
            if old_param.count() == 0:
                p = DefinitionParam(definition=definition, 
                                name=param['new_name'], 
                                readable_name=param['old_name'], 
                                range_start=float(param['min']),
                                range_end=float(param['max']),
                                order=order,
                                index=order)  
                p.save()
                order=order+1
        
        new_params = DefinitionParam.objects.filter(definition=definition)
        for new_param in new_params:
            new_param.index = new_param.order
            new_param.save()

        return True
    
    def param_names(self):
        return map(lambda x: x.name, self.definitionparam_set.all().order_by('index','pk'))
    
    def set_file_name(self):
        parts = self.current_file_name.split('.')
        self.file_name = "%s%s.%s" % (parts[0],self.ADJUSTED_SUFFIX ,parts[1])
        
    def set_defaults(self):
        parts = self.uploaded_file_name.split('.',2)
        self.name = parts[0]
        self.scene_file = 'cases_testing.3dm'
        self.active = True
        self.use_cache = True
        self.default_material = get_material()
        materials = Material.objects.all()
        for m in materials:
            dm = DefinitionMaterial(definition=self, material = m)
            dm.save()
    
    def check_3dm(self):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, calling_format=OrdinaryCallingFormat())
        bucket = conn.get_bucket(settings.BASE_MODELS_BUCKET)
        k = Key(bucket)
        items = Item.objects.filter(definition=self)
        for item in items:
            k.key = item.get_3dm_key()
            exists = k.exists()
            print "%s %s" % (item.uuid, exists)
            if exists:
                item.has_3dm = True
                item.save()    
                    
    def __unicode__(self):
        return self.name

class DefinitionMaterial(models.Model):
    definition = models.ForeignKey(GhDefinition)
    material = models.ForeignKey(Material)
    def __unicode__(self):
        return "%s %s %s" % (self.definition.file_name, self.definition.id, self.material.name)
        
class DefinitionParam(models.Model):
    default_values = [0,0.2,0.4,0.6,0.8,1]
    name = models.CharField(max_length=100)
    readable_name = models.CharField(max_length=200)
    definition = models.ForeignKey(GhDefinition)
    index = models.IntegerField(default=0)
    order = models.IntegerField()
    stage = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    range_start = models.FloatField(default=0)
    range_end = models.FloatField(default=1)
    rendering_view = models.CharField(max_length=200, null=True, blank=True)
    values = PickledObjectField(null=True, blank=True)
    INTEGER = 'IN'
    FLOAT = 'FL'
    STRING = 'ST'
   
    STATUS_CHOISES = ((INTEGER,'Integer'), (FLOAT, 'Float'), (STRING, 'String'))
    param_type = models.CharField(max_length=2,
                              choices=STATUS_CHOISES,
                              default=FLOAT)

    def get_initial_value(self):
        values = self.get_values()
        initial_index = int(math.floor((len(values)-1)/2))-1
        return values[initial_index]
    
    def get_values(self):
        if isinstance(self.values, list):
            return self.values
        else:
            return map(lambda x: self.map_value(x), self.default_values)
    
    def map_value(self, x):
        print "X %s" % x
        v = (x*(self.range_end-self.range_start))+self.range_start
        if self.param_type == self.INTEGER:
            return(math.floor(v))
        print "V %s" % v
        return v

    def __unicode__(self):
        #p = Product.objects.get(pk=self.definition.product)
        return "%s - %s" % (self.definition.id, self.readable_name)
    
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image_url = models.CharField(max_length=100, null=True)
    parent = models.ForeignKey('self', null=True)
    definition = models.ForeignKey(GhDefinition, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    params = PickledObjectField(null=True)
    textParam = models.CharField(max_length=100, null=True)
    sent = models.BooleanField()
    selected = models.BooleanField()
    uuid = models.CharField(max_length=100, null=True)
    parent_distance = models.CharField(max_length=20)
    material = models.CharField(max_length=20, default="Gold")
    param_hash = models.CharField(max_length=100, null=True, db_index=True)
    base_param_hash = models.CharField(max_length=100, null=True, db_index=True)
    rendering_view = models.CharField(max_length=200, default="")
    has_3dm = models.BooleanField(default=False)
    
    CREATED = 'CR'
    SENT = 'SE'
    FINISHED = 'FI'
    ERROR = 'ER'
    
    STATUS_CHOISES = ((CREATED,'Created'), (SENT, 'Sent'), (FINISHED, 'Finished'), (ERROR, 'Error'))
    status = models.CharField(max_length=2,
                              choices=STATUS_CHOISES,
                              default=CREATED)
    
    num_trials = models.IntegerField(default=0)
        
    def __unicode__(self):
        return str(self.id)
        
    def get_3dm_key(self):
        return self.uuid + '.3dm'
    
class ExplorerConfig(models.Model):
    id = models.AutoField(primary_key=True)
    k = models.CharField(max_length=32)
    v = models.CharField(max_length=256)
    def __unicode__(self):
        return self.k

class AppData(models.Model):
    name = models.CharField(max_length=32)
    last_wakeup = models.DateTimeField()
# Create your models here.
