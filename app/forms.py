from django import forms


class NintendoSessionForm(forms.Form):
    token = forms.CharField(widget=forms.Textarea)


class NintendoSessionRequestForm(forms.Form):
    url = forms.CharField(widget=forms.Textarea)
