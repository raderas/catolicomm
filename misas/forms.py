from django import forms
from misas.models import Templo

class TemploForm(forms.ModelForm):
    class Meta:
        model=Templo
        fields=['nombre','direccion','alias']