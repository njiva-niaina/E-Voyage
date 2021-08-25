from django.db import models
from django.db.models import F
from imagekit.models import ImageSpecField
from pilkit.processors import Thumbnail
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify

class Fonctions(models.Model):
    nom_fonction = models.CharField(max_length=20)
    salaire_fonction = models.IntegerField()
    def __str__(self):
        return self.nom_fonction
    class Meta:
        verbose_name = 'Fonction'
        verbose_name_plural = 'Fonctions'
        ordering = ['nom_fonction']

class Employees(models.Model):
    photo_employee = models.ImageField(upload_to='images/employee/%Y/%m/%d', null=True, blank=True)
    nom_employee = models.CharField(max_length=20)
    prenom_employee = models.CharField(max_length=20)
    fonction_employee = models.ForeignKey(Fonctions, on_delete=models.CASCADE)
    telephone_employee = models.CharField(max_length=20)
    email_employee = models.EmailField()
    localisation_employee = models.CharField(
        max_length=20,
        choices=(
            ('antananarivo','Antananarivo'),
            ('antsiranana','Antsiranana'),
            ('fianarantsoa','Fianarantsoa'),
            ('toamasina','Toamasina'),
            ('mahajanga','Mahajanga'),
            ('toliara','Toliara'),
        )
    )
    adresse_employee = models.CharField(max_length=20)    
    disponibilite_employee = models.BooleanField(default=True)
    def __str__(self):
        return str("{} {}".format(self.nom_employee,self.prenom_employee))
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['nom_employee','prenom_employee']
    @property
    def image_preview(self):
        if self.photo_employee:
            return mark_safe('<img src="{}" width="30px" height="30px" >'.format(self.photo_employee.url))
        return ""
    
class Marques(models.Model):
    nom_marque = models.CharField(max_length=20)
    def __str__(self):
        return self.nom_marque
    class Meta:
        verbose_name = 'Marque'
        verbose_name_plural = 'Marques'
        ordering = ['nom_marque']

class Vehicules(models.Model):
    photo_vehicule = models.ImageField(upload_to='images/vehicle/%Y/%m/%d/', null=True, blank=True)
    immatriculation_vehicule = models.CharField(max_length=20)
    marque_vehicule = models.ForeignKey(Marques, on_delete=models.CASCADE)
    modele_vehicule = models.CharField(max_length=20)
    moteur_vehicule = models.CharField(max_length=20)
    capacite_vehicule = models.IntegerField()
    disponibilite_vehicule = models.BooleanField(default=True)
    def __str__(self):
        return self.immatriculation_vehicule
    class Meta:
        verbose_name = 'Vehicule'
        verbose_name_plural = 'Vehicules'
        ordering = ['marque_vehicule']
    @property
    def vehicule_image_preview(self):
        if self.photo_vehicule:
            return mark_safe("<img src={} width=30 height=30>".format(self.photo_vehicule.url))
        return ""

class Images(models.Model):
    titre_image = models.CharField(max_length=20)
    image = models.ImageField(upload_to='images/%Y/%m/%d/', null=True, blank=True)
    image_moyen = ImageSpecField(
        source='image', 
        processors=[Thumbnail(160,205)],
        format='JPEG',
        options={'quality':60}
    )
    image_petit = ImageSpecField(
        source='image',
        processors=[Thumbnail(160,160)],
        format='JPEG',
        options={'quality':60}
    )
    def __str__(self):
        return self.titre_image
    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
    
class Lieux(models.Model):
    nom_lieu = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.nom_lieu
    class Meta:
        verbose_name = 'Lieu'
        verbose_name_plural = 'Lieux'
        ordering = ['nom_lieu']

class Voyages(models.Model):
    photo_autres = models.ManyToManyField(Images)
    couverture_voyage = models.ImageField(upload_to='images/%Y/%m/%d/', null=True, blank=True)
    couverture_grand = ImageSpecField(
        source='couverture_voyage',
        processors=[Thumbnail(700,350)],
        format='JPEG',
        options={'quality':60}
    )
    couverture_grand2 = ImageSpecField(
        source='couverture_voyage',
        processors=[Thumbnail(400,559)],
        format='JPEG',
        options={'quality':60}
    )
    couverture_moyen = ImageSpecField(
        source='couverture_voyage',
        processors=[Thumbnail(160,205)],
        format='JPEG',
        options={'quality':60}
    )
    couverture_petit = ImageSpecField(
        source='couverture_voyage',
        processors=[Thumbnail(160,136)],
        format='JPEG',
        options={'quality':60}
    )
    nom_voyage = models.CharField(max_length=20)
    prix_voyage = models.IntegerField()
    place_voyage = models.PositiveSmallIntegerField()
    date_voyage = models.DateField(auto_now=False, auto_now_add=False)
    duree_voyage = models.IntegerField()
    lieu_voyage = models.ForeignKey(Lieux, on_delete=models.CASCADE)
    vehicule_voyage = models.ForeignKey(Vehicules, on_delete=models.CASCADE)
    chauffeur_voyage = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name="driver")
    responsable_voyage = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name="responsible")
    description_voyage = models.TextField()
    slug = models.SlugField(blank=True)
    def __str__(self):
        return str("{} - {}".format(self.nom_voyage,self.lieu_voyage.nom_lieu))
    def save(self, *args, **kwargs):
        if not self.id:
            if not self.slug:
                self.slug = slugify(str(self.nom_voyage)+"-"+str(self.lieu_voyage.nom_lieu))
            if self.place_voyage > self.vehicule_voyage.capacite_vehicule:
                self.place_voyage = self.vehicule_voyage.capacite_vehicule
        super(Voyages, self).save(*args, **kwargs)
    class Meta:
        verbose_name = 'Voyage'
        verbose_name_plural = 'Voyages'

class Reservations(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    voyage = models.ForeignKey(Voyages, on_delete=models.CASCADE)
    nombre_place = models.IntegerField()
    contact = models.CharField(max_length=20, blank=True, null=True)
    paiement = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.id:
            place_libre = self.voyage.place_voyage
            if self.nombre_place > place_libre:
                self.nombre_place = place_libre
            Voyages.objects.filter(id=self.voyage.id).update(place_voyage=F('place_voyage')-self.nombre_place)
        super(Reservations, self).save(*args, **kwargs)
    def total(self):
        return self.nombre_place * self.voyage.prix_voyage
    def __str__(self):
        return str("{} - {}".format(self.client.username, self.voyage.nom_voyage))
    class Meta:
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        ordering = ['client']
