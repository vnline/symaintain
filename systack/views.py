#!-*- coding=utf-8 -*-

from django.shortcuts import render_to_response,Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.messages import api as messages,constants as message
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from form import *


@login_required(login_url='account_login')
def index(request):
    '''首页'''
    if request.user.is_authenticated():
        user = request.user
        return render_to_response('index.html',{'user':user},context_instance=RequestContext(request))
    else:
        #user = request.user
        return HttpResponseRedirect(reverse('account_login'))
    #return render_to_response('index.html',{'user':user},context_instance=RequestContext(request))


def validate_login(request, username, password):
    '''验证用户登录'''
    return_value = False
    user = authenticate(username=username,password=password)
    if user:
        if user.is_active:
            auth_login(request,user)
            return_value = True
        else:
            messages.add_message(request, message.INFO, _(u'此账户尚未激活，请联系管理员'))
    else:
        messages.add_message(request, message.INFO, _(u'此账户不存在，请联管理员'))
    return return_value

def login(request):
    '''用户登录页'''
    template_var = {}
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST.copy())
        if form.is_valid():
            validate_login(request, form.cleaned_data["username"], form.cleaned_data["password"])
            return HttpResponseRedirect(reverse('index'))
    template_var["form"] = form
    return render_to_response('login.html', template_var, context_instance=RequestContext(request))


def logout(request):
    '''用户注销页'''
    auth_logout(request)
    return HttpResponseRedirect(reverse('account_login'))

@login_required(login_url='account_login')
def schedule(request):
    schedules = Schedule.objects.all().order_by('-id')
    paginator = Paginator(schedules ,10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        schedules = paginator.page(page)
    except :
        schedules = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        schedule = Schedule()
        form = ScheduleForm(request.POST,instance=schedule)
        if form.is_valid():
            base = form.save(commit=False)
            base.created_by = request.user
            base.mtime = timezone.now()
            base.save()
    t = get_template('schedule.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@login_required(login_url='account_login')
def updatesch(request,itemid):
    schedule_instance = Schedule.objects.get(id=itemid)
    form = ScheduleForm(request.POST or None,instance=schedule_instance)
    if form.is_valid():
        form = form.save(commit=False)
        if form.open_time < timezone.now():
            form.status = 'True'
        form.save()
        return HttpResponseRedirect(reverse('schedule'))
    t = get_template('schedule_edit.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@login_required(login_url='account_login')
def delete(request,itemid):
    schedules = Schedule.objects.get(id=itemid)
    schedules.delete()
    return HttpResponseRedirect(reverse('schedule'))

@login_required(login_url='account_login')
def finish(request,itemid):
    schedule_instance = Schedule.objects.get(id=itemid)
    schedule_instance.deployed_by = unicode(request.user)
    schedule_instance.deploy = True
    if schedule_instance.open_time < timezone.now():
        schedule_instance.status = 'True'
    schedule_instance.save()
    return HttpResponseRedirect(reverse('schedule'))


@login_required(login_url='account_login')
def hotupdate(request):
    hots = Hot_update.objects.all().order_by('-id')
    paginator = Paginator(hots ,10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        hots = paginator.page(page)
    except :
        hots = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        hots = Hot_update()
        form = HotupdateForm(request.POST,instance=hots)
        if form.is_valid():
            base = form.save(commit=False)
            base.created_by = unicode(request.user)
            base.mtime = timezone.now()
            base.save()
    t = get_template('hotupdate.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))




