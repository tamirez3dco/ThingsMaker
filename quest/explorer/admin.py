from explorer.models import Item, GhDefinition, ExplorerConfig, AppData, DefinitionParam, Material, DefinitionMaterial
from explorer.explore.controller import Base as Controller
from lfs.catalog.models import Product
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from django.contrib import admin
from django import forms
import cPickle as pickle
from django.utils import simplejson
import uuid

def preprocess_items(modeladmin, request, queryset):
    definition = queryset[0]
    controller = Controller('Default', 1)
    controller.preprocess_definition(definition)
    
preprocess_items.short_description = "Preprocess Items"
      
def send_background_items(modeladmin, request, queryset):
    controller = Controller('Default', 1)
    controller.send_background_items()
    
send_background_items.short_description = "Send Background Items"

def set_sent(modeladmin, request, queryset):
    #definition = queryset[0]
    #items = Item.objects.filter(sent=False, definition=definition)
    items = Item.objects.all()
    print items.count()
    for item in items:
        item.status=Item.FINISHED
        item.save()
        
set_sent.short_description = "Set all items as sent"
 
def process_ghx(modeladmin, request, queryset):
    definition = queryset[0]
    controller = Controller()
    controller.process_ghx(definition)
process_ghx.short_description = "Process GHX file"
      
class PickleField(forms.CharField):
    def clean(self, value):
        #try:
        return simplejson.loads(str(value))
        #except:
        #    raise ValidationError
        
class GhDefinitionAdminForm( forms.ModelForm ):  
    name = forms.CharField( max_length = 255, required = False ) 
    file_name = forms.CharField( max_length = 255, required = True )
    scene_file = forms.CharField( max_length = 255, required = True )
    active = forms.BooleanField(initial=True, required=False)
    accepts_text_params = forms.BooleanField(initial=False,required=False)
    default_material = forms.ModelChoiceField(Material.objects.all())
    use_cache = forms.BooleanField(initial=True,required=False)
    base_definition = forms.ModelChoiceField(GhDefinition.objects.all(),required=False)
    uploaded_file = forms.FileField(required=False)
    current_file_name = forms.CharField( max_length = 255, required = False ) 
    uploaded_file_name = forms.CharField( max_length = 255, required = False ) 

class GhDefinitionAddAdminForm( forms.ModelForm ): 
    class Meta:
        model = GhDefinition
    name = forms.CharField( max_length = 255, required = False ) 
    file_name = forms.CharField( max_length = 255, required = False )
    scene_file = forms.CharField( max_length = 255, required = False )
    active = forms.BooleanField(initial=True, required=False)
    accepts_text_params = forms.BooleanField(initial=False,required=False)
    default_material = forms.ModelChoiceField(Material.objects.all(), initial=Material.objects.all()[0], required = False )
    use_cache = forms.BooleanField(initial=True,required=False)
    base_definition = forms.ModelChoiceField(GhDefinition.objects.all(),required=False)
    uploaded_file = forms.FileField(required=False)
    current_file_name = forms.CharField( max_length = 255, required = False ) 
    uploaded_file_name = forms.CharField( max_length = 255, required = False ) 
        
class GhDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_file_name','file_name','scene_file','active','accepts_text_params' )
    fields = ('uploaded_file','name','uploaded_file_name','file_name','base_definition','scene_file','active','accepts_text_params', 'default_material','use_cache')
    form = GhDefinitionAdminForm
    actions = [preprocess_items, send_background_items, set_sent, process_ghx]
    def save_model(self, request, obj, form, change):
        form.default_material = Material.objects.all()[1]
        obj.default_material = Material.objects.all()[1]
        super(GhDefinitionAdmin, self).save_model(request, obj, form, change)
        if change==False:
            obj.set_defaults()
            p = Product(name=obj.name, slug=uuid.uuid1(), ghdefinition=obj, sub_type=PRODUCT_WITH_VARIANTS, active=False)
            p.save()
            
        if "uploaded_file" in form.changed_data:
            controller = Controller()
            obj.set_file_name()
            controller.process_ghx(obj)
            obj.save()
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:       
            self.fields = ('uploaded_file',)
            return GhDefinitionAddAdminForm
            #return super(GhDefinitionAdmin, self).get_form(request, obj, **kwargs)
        else:
            self.fields = ('uploaded_file','name','uploaded_file_name','file_name','base_definition','scene_file','active','accepts_text_params', 'default_material','use_cache')
            return super(GhDefinitionAdmin, self).get_form(request, obj, **kwargs)

    

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id','definition','status','params','base_param_hash','textParam','uuid', 'image_url')
    list_filter = ('definition','status')  
    fields = ('definition','status','params','base_param_hash','textParam','uuid', 'image_url') 

class DefinitionParamAdmin(admin.ModelAdmin):
    list_display = ('readable_name', 'name', 'definition', 'index','order', 'range_start', 'range_end', 'values', 'active','rendering_view')
    list_filter = ('definition',)   
    fields = ('readable_name', 'name', 'definition', 'index','order', 'range_start', 'range_end', 'values', 'active','rendering_view')
    
class DefinitionMaterialAdmin(admin.ModelAdmin):
    list_display = ('definition', 'material')
    list_filter = ('definition', 'material')   
    #fields = ('readable_name', 'name', 'definition', 'order', 'range_start', 'range_end', 'values', 'active')
    

admin.site.register(GhDefinition, GhDefinitionAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(ExplorerConfig)
admin.site.register(AppData)
admin.site.register(DefinitionParam,DefinitionParamAdmin)
admin.site.register(Material)
admin.site.register(DefinitionMaterial,DefinitionMaterialAdmin)
