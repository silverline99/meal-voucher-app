from django.db import models


class Distribution(models.Model):
    kvantita = models.IntegerField(null=True)
    hodnota = models.IntegerField(null=True)
    jmeno = models.CharField(max_length=50, null=True)
    prijmeni = models.CharField(max_length=50, null=True)
    mesic_vydani = models.CharField(max_length=10, null=True)
    narok_v_mesici = models.IntegerField(null=True)
    suma = models.IntegerField(null=True)
    chyba_distribuce = models.CharField(max_length=1, null=True)


class MonthOfIssue(models.Model):
    """
    Enables to use the parameter month of issue
    """
    mesic_vydani = models.CharField(max_length=8, blank=False, null=False)


class EmployeeInput(models.Model):
    jmeno = models.CharField(max_length=50, blank=False, null=False)
    prijmeni = models.CharField(max_length=50, blank=False, null=False)
    datum_narozeni = models.DateField(max_length=50, blank=True, null=True)
    zavod = models.CharField(max_length=50, blank=False, null=False)
    narok = models.IntegerField('Nárok', blank=True, null=True)
    vlozeno = models.DateTimeField(auto_now_add=True)


class MealVoucherWarehouse(models.Model):
    name = 'Stravenka'
    kvantita = models.IntegerField()
    hodnota = models.IntegerField()
    suma = models.IntegerField(null=True)


class MealVoucherInput(models.Model):
    name = 'Stravenka'
    kvantita = models.IntegerField()
    hodnota = models.IntegerField()




















"""class MesicVydani(models.Model):
    mesic_vydani = models.CharField(max_length=8, blank=False, null=False)


class ZamestnanecInput(models.Model):
    jmeno = models.CharField(max_length=50, blank=False, null=False)
    prijmeni = models.CharField(max_length=50, blank=False, null=False)
    datum_narozeni = models.DateField(max_length=50, blank=False, null=False)
    narok = models.IntegerField('Nárok', blank=True, null=True)
    vlozeno = models.DateTimeField(auto_now_add=True)"""
