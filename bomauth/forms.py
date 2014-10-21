from django import forms
from django.contrib.auth.models import User

class UserRegisterForm(forms.Form):
   first_name = forms.CharField(1000, required=True)
   last_name = forms.CharField(1000)
   username = forms.CharField(1000)
   email = forms.EmailField(1000)
   password = forms.CharField(widget=forms.PasswordInput)
  
   def clean(self):
      cleaned_data = super(UserRegisterForm, self).clean()

   def clean_email(self):
      username = self.cleaned_data.get('username')
      email = self.cleaned_data.get('email')

      if email and User.objects.filter(email=email).exclude(username=username).count():
         raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
         return email

   def clean_username(self):
      username = self.cleaned_data.get('username')
      email = self.cleaned_data.get('email')

      if username and User.objects.filter(username=username).count():
         raise forms.ValidationError('This username is already in use. Please supply a different username.')
         return email

class UpdateProfile(forms.Form):
   username = forms.CharField(required=True)
   email = forms.EmailField(required=True)
   first_name = forms.CharField(required=False)
   last_name = forms.CharField(required=False)

class Meta:
   model = User
   fields = ('username', 'email', 'first_name', 'last_name')

   def clean_email(self):
      username = self.cleaned_data.get('username')
      email = self.cleaned_data.get('email')

      if email and User.objects.filter(email=email).exclude(username=username).count():
         raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
         return email

   def save(self, commit=True):
      user = super(RegistrationForm, self).save(commit=False)
      user.email = self.cleaned_data['email']

      if commit:
         user.save()

      return user
