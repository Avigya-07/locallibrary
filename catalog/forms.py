import datetime
from django import forms
from django.core.exceptions import ValidationError
from .models import plant
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

class plantForm(forms.ModelForm):
    class Meta:
        model=plant
        fields='__all__'

class NewUserForm(UserCreationForm):
    email=forms.EmailField(required=True)
    
    class Meta:
        model=User
        fields=["username","email","password1","password2"]

        def save(self,commit=True):
            user=super(NewUserForm, self).save(commit=False)
            user.email=self.cleaned_data['email']
            if commit:
                user.save()
            return user


