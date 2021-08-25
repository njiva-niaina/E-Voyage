from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Employees, Fonctions, Images, Lieux, Marques, Reservations, Vehicules, Voyages
from django.db.models import F,Q
from django.contrib.admin import AdminSite

# Setting functions
class FonctionAdmin(admin.ModelAdmin):
    list_display = ['nom_fonction','salaire_fonction']
    list_display_links = None
    list_editable = ['salaire_fonction']
admin.site.register(Fonctions, FonctionAdmin)

# Setting employees
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview',
        'nom_employee',
        'prenom_employee',
        'fonction_employee',
        'telephone_employee',
        'adresse_employee',
        'disponibilite_employee'
    ]
    list_filter = ['fonction_employee']
    search_fields = ['nom_employee','prenom_employee']
    list_editable = ['disponibilite_employee']
    def image_preview(self, obj):
        return obj.image_preview
    image_preview.short_description = 'Image'
    image_preview.allow_tags = True
admin.site.register(Employees, EmployeeAdmin)

# Setting vehicles
class VehiculeAdmin(admin.ModelAdmin):
    list_display = [
        'vehicule_image_preview',
        'marque_vehicule',
        'modele_vehicule',
        'immatriculation_vehicule',
        'capacite_vehicule',
        'disponibilite_vehicule'
    ]
    list_filter = ['marque_vehicule']
    list_editable = ['disponibilite_vehicule']
    search_fields = ['immatriculation_vehicule']
    actions = ['delete_selected']
    def vehicule_image_preview(self,obj):
        return obj.vehicule_image_preview
    vehicule_image_preview.short_description = 'Image'
    vehicule_image_preview.allow_tags = True
admin.site.register(Vehicules, VehiculeAdmin)

# Setting images
class ImageAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
admin.site.register(Images, ImageAdmin)
    
# Setting voyages
class VoyageAdmin(admin.ModelAdmin):
    list_display = [
        'nom_voyage',
        'duree_voyage',
        'lieu_voyage',
        'date_voyage',
        'prix_voyage',
        'chauffeur_voyage',
        'responsable_voyage',
        'place_voyage',
        'vehicule_voyage'
    ]
    list_editable = [
        'duree_voyage',
        'date_voyage',
        'prix_voyage',
        'responsable_voyage',
        'vehicule_voyage',
        'chauffeur_voyage'
    ]
    # list_display_links = None
    search_fields = ['nom_voyage','lieu_voyage']
    actions = ['delete_selected']
    # Customize formfields for voyage_driver & voyage_responsible 
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vehicule_voyage":
            kwargs["queryset"] = Vehicules.objects.filter(disponibilite_vehicule=True)
        if db_field.name == "chauffeur_voyage":
                kwargs["queryset"] = Employees.objects.filter(
                    disponibilite_employee=True,
                    fonction_employee__id=3,
                )
        if db_field.name == "responsable_voyage":
                kwargs["queryset"] = Employees.objects.filter(
                    disponibilite_employee=True).exclude(
                        fonction_employee__id=3
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)     
admin.site.register(Voyages, VoyageAdmin)

# Setting reservations
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'client', 
        'voyage', 
        'nombre_place', 
        'contact',
        'total',
        'paiement'
    ]
    list_display_links = None
    list_editable = ['paiement']
    list_filter = ['voyage']
    actions = ['cancel_reservation']
    search_fields = ['client__username']
    # Define cancel actions
    def cancel_reservation(self, request, queryset):
        q = queryset.values('voyage_id')
        r = queryset.values('nombre_place')
        for i in range(len(q)):
            Voyages.objects.filter(id=q[i]['voyage_id']).update(
                place_voyage=F('place_voyage')+r[i]['nombre_place']
            )
        queryset.delete()
    cancel_reservation.short_description = "Annuler reservation"
    # Customize formfield for voyage
    def formfield_for_foreignkey(self,db_field,request,**kwargs):
        if db_field.name == "voyage":
            kwargs["queryset"] = Voyages.objects.filter(place_voyage__gt=0)
        return super().formfield_for_foreignkey(db_field,request,**kwargs)
admin.site.register(Reservations, ReservationAdmin)

# Register brand
class MarqueAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
admin.site.register(Marques, MarqueAdmin)

# Register locations
class LieuAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
admin.site.register(Lieux, LieuAdmin)

# Unergister Group
admin.site.unregister(Group)

# Disable delete_selected
admin.site.disable_action('delete_selected')

# Customize admin site
AdminSite.site_header = "Discovery administration"
AdminSite.site_title = "Control panel"
AdminSite.index_title = "Discovery"
