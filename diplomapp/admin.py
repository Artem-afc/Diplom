from django.contrib import admin
from .models import District, Building, Apartment, ApartmentImage, InterestRate, InfrastructureItem

class ApartmentImageInline(admin.TabularInline):
    model = ApartmentImage
    extra = 3

class ApartmentAdmin(admin.ModelAdmin):
    inlines = [ApartmentImageInline]
    list_display = ('building', 'bedrooms', 'price', 'image', 'is_sold', 'allow_multiple_purchases', 'finishing')
    list_filter = ('is_sold', 'allow_multiple_purchases', 'finishing')
    search_fields = ('building__address', 'description', 'finishing')
    ordering = ('building__address', 'bedrooms')

class InterestRateAdmin(admin.ModelAdmin):
    list_display = ('calculator_type', 'rate')

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class InfrastructureItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'building')
    list_filter = ('type', 'building')
    search_fields = ('name', 'address')

admin.site.register(District, DistrictAdmin)
admin.site.register(Building)
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(InterestRate, InterestRateAdmin)
admin.site.register(InfrastructureItem, InfrastructureItemAdmin)