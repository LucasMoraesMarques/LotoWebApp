from django import forms
from lottery.models import Lottery, Collection, LOTTERY_CHOICES
from django.contrib.auth.forms import UserCreationForm, User
from django.core.exceptions import ValidationError



class GameGeneratorForm(forms.Form):
    def __init__(self, loto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(loto)
        loto = Lottery.objects.get(id=loto)
        choicesNPlayed = [(str(i), i) for i in loto.possiblesChoicesRange]
        choicesNFixed = [(str(i), i) for i in range(1, loto.numbersRangeLimit + 1)]
        choicesNRemoved = [(str(i), i) for i in range(1, loto.numbersRangeLimit + 1)]
        self.fields["nPlayed"] = forms.ChoiceField(
            widget=forms.RadioSelect, choices=choicesNPlayed
        )
        self.fields["nFixed"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=choicesNFixed
        )
        self.fields["nRemoved"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=choicesNRemoved
        )


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Primeiro Nome')
    first_name.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite seu primeiro nome',
         'aria-label': 'Primeiro Nome', 'aria-describedby': "first-name-addon"})
    last_name = forms.CharField(label='Último Nome')
    last_name.widget.attrs.update({'class': 'form-control', 'required': True, 'placeholder': 'Digite seu último nome',
                                   'aria-label': 'Último Nome', 'aria-describedby': "last-name-addon"})
    username = forms.CharField(label='Usuário', min_length=5, max_length=50)
    username.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite seu nome de usuário',
         'aria-label': 'Nome de Usuário', 'aria-describedby': "username-addon"})
    email = forms.EmailField(label='Digite seu email')
    email.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite seu email', 'aria-label': 'Email',
         'aria-describedby': "email-addon"})
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password1.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite sua senha', 'aria-label': 'Senha',
         'aria-describedby': "password1-addon"})
    password2 = forms.CharField(label='Confirme sua senha', widget=forms.PasswordInput)
    password2.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite sua senha novamente',
         'aria-label': 'Confirmação de Senha', 'aria-describedby': "password2-addon"})

    def username_clean(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username):
            raise ValidationError('Já existe um cadastro com esse nome de usuário')
        return username

    def email_clean(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email):
            raise ValidationError('Já existe um cadastro com esse email')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise ValidationError("As senhas digitadas não são iguais")
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['first_name']
        user.save()
        return user


class LoginForm(forms.ModelForm):
    email = forms.EmailField(label='Digite seu email')
    email.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite seu email', 'aria-label': 'Email',
         'aria-describedby': "email-addon"})
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password.widget.attrs.update(
        {'class': 'form-control', 'required': True, 'placeholder': 'Digite sua senha', 'aria-label': 'Senha',
         'aria-describedby': "password1-addon"})

    class Meta:
        model = User
        fields = ['email', 'password']


class CreateCollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'lottery']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(max_length=50, label='Nome da Coleção')
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['lottery'].queryset = Lottery.objects.all()
        self.fields['lottery'].label = 'Loteria'
        self.fields['lottery'].widget.attrs.update({'class': 'form-control'})

    def save(self, user):
        collection = Collection.objects.create(
            name=self.cleaned_data['name'],
            lottery=self.cleaned_data['lottery'],
            user=user
        )
        collection.save()
        return collection


class UploadCollectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(max_length=50, label='Nome da Coleção')
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'] = forms.FileField()
        self.fields['file'].widget.attrs.update({'class': 'form-control'})

