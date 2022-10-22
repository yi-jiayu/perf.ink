from django import forms


class NintendoSessionForm(forms.Form):
    token = forms.CharField()


class NintendoSessionRequestForm(forms.Form):
    url = forms.CharField()
