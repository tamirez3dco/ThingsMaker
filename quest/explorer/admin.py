from explorer.models import Item, GhDefinition, ExplorerConfig, AppData, DefinitionParam, Material, DefinitionMaterial
from django.contrib import admin
from django import forms
import cPickle as pickle
from django.utils import simplejson

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
    #use_cache = forms.BooleanField(initial=True,required=False)
    
class GhDefinitionAdmin(admin.ModelAdmin):
    fields = ('file_name','scene_file','product','active','param_names','accepts_text_params', 'default_material','use_cache')
    form = GhDefinitionAdminForm
#    def save_model(self, request, obj, form, change):
#        obj.file_name = form.cleaned_data['file_name']
#        obj.active = form.cleaned_data['active']
#        obj.set_param_names(form.cleaned_data['param_names'])
#        obj.save()    

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id','definition')
          
admin.site.register(GhDefinition, GhDefinitionAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(ExplorerConfig)
admin.site.register(AppData)
admin.site.register(DefinitionParam)
admin.site.register(Material)
admin.site.register(DefinitionMaterial)
