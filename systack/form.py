#!-*- coding=utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from systack.models import Schedule,Hot_update,Deploy,Operation

class LoginForm(forms.Form):

    username=forms.CharField(label=(u"登录账号"), widget=forms.TextInput(attrs={'placeholder':'Username', 'class':'input-block-level'}))
    password=forms.CharField(label=(u"登录密码"), widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':'input-block-level'}))

class RegisterForm(forms.Form):
    '''注册表单'''
    username=forms.CharField(label=(u"登录账号"), widget=forms.TextInput(attrs={'placeholder':'登录账号','class':'input-block-level'}))
    email=forms.EmailField(label=(u"邮件地址"), widget=forms.TextInput(attrs={'placeholder':'登录邮箱','class':'input-block-level'}))
    password=forms.CharField(label=(u"登录密码"), widget=forms.PasswordInput(attrs={'placeholder':'登录密码','class':'input-block-level'}))
    repassword=forms.CharField(label=(u"重复登录密码"), widget=forms.PasswordInput(attrs={'placeholder':'重复登录密码','class':'input-block-level'}))

    def clean_username(self):
        '''验证昵称'''
        username = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not username:
            return self.cleaned_data["username"]
        raise forms.ValidationError((u"该昵称已经被使用"))

    def clean_email(self):
        '''验证email'''
        email = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not email:
            return self.cleaned_data["email"]
        raise forms.ValidationError((u"改邮箱已经被使用"))

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        exclude = ('deployed_by','mtime')


class HotupdateForm(ModelForm):
    class Meta:
        model = Hot_update
        exclude = ('hot_status','deployed_by','mtime')

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()