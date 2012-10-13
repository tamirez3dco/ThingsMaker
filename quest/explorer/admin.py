from explorer.models import Item, GhDefinition, ExplorerConfig, AppData, DefinitionParam, Material, DefinitionMaterial
from explorer.explore.controller import Base as Controller
from django.contrib import admin
from django import forms
import cPickle as pickle
from django.utils import simplejson

def preprocess_items(modeladmin, request, queryset):
    definition = queryset[0]
    controller = Controller('near', 'Default', 1)
    controller.preprocess_definition(definition)
    
preprocess_items.short_description = "Preprocess Items"
      
def send_background_items(modeladmin, request, queryset):
    definition = queryset[0]
    controller = Controller('near', 'Default', 1)
    #controller.send_background_items(definition)
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
      
class PickleField(forms.CharField):
    def clean(self, value):
        #try:
        return simplejson.loads(str(value))
        #except:
        #    raise ValidationError
        
class GhDefinitionAdminForm( forms.ModelForm ):    
    file_name = forms.CharField( max_length = 255, required = True )
    scene_file = forms.CharField( max_length = 255, required = True )
    product = forms.IntegerField()
    active = forms.BooleanField(initial=True, required=False)
    param_names = PickleField( max_length = 1000, required = True )
    accepts_text_params = forms.BooleanField(initial=False,required=False)
    default_material = forms.ModelChoiceField(Material.objects.all())
    use_cache = forms.BooleanField(initial=True,required=False)
    base_definition = forms.ModelChoiceField(GhDefinition.objects.all(),required=False)
    
class GhDefinitionAdmin(admin.ModelAdmin):
    fields = ('file_name','base_definition','scene_file','product','active','param_names','accepts_text_params', 'default_material','use_cache')
    form = GhDefinitionAdminForm
    actions = [preprocess_items, send_background_items, set_sent]
#    def save_model(self, request, obj, form, change):
#        obj.file_name = form.cleaned_data['file_name']
#        obj.active = form.cleaned_data['active']
#        obj.set_param_names(form.cleaned_data['param_names'])
#        obj.save()    

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id','definition','status','params','uuid', 'image_url')
    list_filter = ('definition','status')   

class DefinitionParamAdmin(admin.ModelAdmin):
    list_display = ('definition','name','readable_name','order')
    list_filter = ('definition',)   
    
admin.site.register(GhDefinition, GhDefinitionAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(ExplorerConfig)
admin.site.register(AppData)
admin.site.register(DefinitionParam,DefinitionParamAdmin)
admin.site.register(Material)
admin.site.register(DefinitionMaterial)
