import math
from django.db import models
#import cPickle as pickle
from django.utils import simplejson as pickle
from south.modelsinspector import add_introspection_rules
#from lfs.catalog.models import Product
#from lfs.catalog.models import Product

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
    
class GhDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    file_name = models.CharField(max_length=100, null=True)
    active = models.BooleanField()
    scene_file = models.CharField(max_length=100)
    product = models.IntegerField()
    accepts_text_params = models.BooleanField(default=False)
    default_material = models.ForeignKey(Material)
    use_cache = models.BooleanField(default=True)
    base_definition = models.ForeignKey('self', null=True, db_index=True, default=None, blank=True)
    
    def param_names(self):
        return map(lambda x: x.name, self.definitionparam_set.all().order_by('index'))
    
    def __unicode__(self):
        return self.file_name

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
    index = models.IntegerField()
    order = models.IntegerField()
    stage = models.IntegerField()
    active = models.BooleanField()
    range_start = models.FloatField(default=0)
    range_end = models.FloatField(default=1)
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
        initial_index = int(math.floor((len(values)-1)/2))
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
        #return (x*(self.range_end-self.range_start))+self.range_start
#    
#    def get_initial_value(self):
#        values = self.get_values()
#        initial_index = int(math.floor((len(values)-1)/2))
#        return values[initial_index]
    
    def __unicode__(self):
        #p = Product.objects.get(pk=self.definition.product)
        return "%s - %s" % (self.definition.id, self.readable_name)
    
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image_url = models.CharField(max_length=100, null=True)
    parent = models.ForeignKey('self', null=True, db_index=True)
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

#class DefinitionReps(models.Model):
#    definition = models.ForeignKey(GhDefinition)
#    item = models.ForeignKey(GhDefinition)
#    param_name = models.CharField(max_length=100)
#    param_val = 

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
