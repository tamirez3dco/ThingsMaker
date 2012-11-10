# django imports
from django.contrib import admin

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import FilterStep
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.catalog.models import ProductAccessories
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import StaticBlock
from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import Designer
import explorer.tasks
from explorer.explore.controller import Base as Controller

def get_stl(modeladmin, request, queryset):
    #queryset.update(status='p')
    item = queryset[0].get_item()
    controller = Controller('near', 'Default', 1)
    controller.get_stl(item.uuid)
get_stl.short_description = "Get STL"
      

class CategoryAdmin(admin.ModelAdmin):
    """
    """
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
    list_display = ('id','name','definition','parent','slug','sub_type')
    list_filter = ( 'sub_type', )
    actions = [get_stl]
    
admin.site.register(Product, ProductAdmin)


class ImageAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Image, ImageAdmin)


class ProductAccessoriesAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(ProductAccessories, ProductAccessoriesAdmin)


class StaticBlockAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(StaticBlock, StaticBlockAdmin)


class DeliveryTimeAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(DeliveryTime, DeliveryTimeAdmin)


admin.site.register(PropertyGroup)
admin.site.register(Property)
admin.site.register(PropertyOption)
admin.site.register(ProductPropertyValue)
admin.site.register(FilterStep)

admin.site.register(Designer)
