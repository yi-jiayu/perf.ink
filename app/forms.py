from django import forms


class NintendoSessionForm(forms.Form):
    token = forms.CharField(widget=forms.Textarea)
