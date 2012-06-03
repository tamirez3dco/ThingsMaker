from explorer.models import Item, GhDefinition, ExplorerConfig, AppData
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
    
class GhDefinitionAdmin(admin.ModelAdmin):
    fields = ('file_name','scene_file','product','active','param_names')
    form = GhDefinitionAdminForm
#    def save_model(self, request, obj, form, change):
#        obj.file_name = form.cleaned_data['file_name']
#        obj.active = form.cleaned_data['active']
#        obj.set_param_names(form.cleaned_data['param_names'])
#        obj.save()    
        
admin.site.register(GhDefinition, GhDefinitionAdmin)
admin.site.register(Item)
admin.site.register(ExplorerConfig)
admin.site.register(AppData)
