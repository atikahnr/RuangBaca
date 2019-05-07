from django import forms
from rbfilkom.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MultipleForm(forms.Form):
    action = forms.CharField(max_length=60, widget=forms.HiddenInput())


class ImageUploadForm(forms.Form):
    gambar = forms.ImageField()


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class KoleksiForm(forms.ModelForm):
    class Meta:
        model = Koleksi
        fields = ('judul', 'no_panggil', 'kode_eksamplar', 'pengarang', 'penerbit', 'isbn_issn', 'tahun_terbit', 'tempat_terbit', 'jenis_koleksi', 'sumber_koleksi', 'bahasa_koleksi', 'topik_koleksi', 'status_ketersediaan', 'gambar')


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ('rating', 'message')