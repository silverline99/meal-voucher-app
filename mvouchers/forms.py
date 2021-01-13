from django import forms
from . import models


class EmployeeAddForm(forms.ModelForm):
    class Meta:
        model = models.EmployeeInput
        fields = ['jmeno', 'prijmeni', 'zavod']
        jmeno = forms.CharField(disabled=True)
    #geeks_field = forms.CharField(disabled=True)
    #prijmeni = forms.CharField(disabled=True) FUNGUJE KDYŽ ODSTRANÍM KŘÍŽEK


class MealVoucherAddForm(forms.ModelForm):
    class Meta:
        model = models.MealVoucherInput
        fields = ['kvantita', 'hodnota']


class MonthOfIssueInputForm(forms.ModelForm):
    class Meta:
        model = models.MonthOfIssue
        fields = ['mesic_vydani']