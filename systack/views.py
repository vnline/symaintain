#!-*- coding=utf-8 -*-

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
from django.views.decorators.csrf import csrf_exempt
from symaintain import settings
#from mc_salt.master.lib import client
from form import *
from models import *
import os


@login_required(login_url='account_login')
def index(request):
    '''首页'''
    if request.user.is_authenticated():
        user = request.user
        #return render_to_response('index.html',{'user':user},context_instance=RequestContext(request))
        t = get_template('systack/index.html')
        c = RequestContext(request,locals())
        return HttpResponse(t.render(c))
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
    #return render_to_response('login.html', template_var, context_instance=RequestContext(request))
    t = get_template('systack/login.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))


def logout(request):
    '''用户注销页'''
    auth_logout(request)
    return HttpResponseRedirect(reverse('account_login'))

@login_required(login_url='account_login')
def schedule(request):
    if request.method == 'POST':
        schedule = Schedule()
        form = ScheduleForm(request.POST,instance=schedule)
        if form.is_valid():
            base = form.save(commit=False)
            base.created_by = request.user
            base.mtime = timezone.now()
            base.save()
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
    t = get_template('systack/schedule.html')
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
    t = get_template('systack/schedule_edit.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@login_required(login_url='account_login')
def delete(request,itemid):
    if request.GET.get('itemid',''):
        schedules = Schedule.objects.get(id=itemid)
        schedules.delete()
        return HttpResponseRedirect(reverse('schedule'))
    else:
        return HttpResponseRedirect(reverse('error'))

@login_required(login_url='account_login')
def finish(request,itemid):
    if request.GET.get('itemid',''):
        schedule_instance = Schedule.objects.get(id=itemid)
        schedule_instance.deployed_by = unicode(request.user)
        schedule_instance.deploy = True
        if schedule_instance.open_time < timezone.now():
            schedule_instance.status = 'True'
        schedule_instance.save()
        return HttpResponseRedirect(reverse('schedule'))
    else:
        return HttpResponseRedirect(reverse('error'))

@login_required(login_url='account_login')
def deploy(request):
    if request.method == 'POST':
        deploy = Deploy()
        form = DeployForm(request.POST,instance=deploy)
        if form.is_valid():
            base = form.save(commit=False)
            print base.importdb,base.cgm
            base.deployed_by = request.user
            base.mtime = timezone.now()
            base.save()
    deploys = Deploy.objects.all().order_by('-id')
    paginator = Paginator(deploys ,10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        deploys = paginator.page(page)
    except :
        deploys = paginator.page(paginator.num_pages)
    t = get_template('systack/deploy.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

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
        form = Hot_updateForm(request.POST,instance=hots)
        val = request.POST['files'].split(' ')

        if form.is_valid():
            base = form.save(commit=False)
            base.files = request.POST['files']
            base.created_by = unicode(request.user)
            base.mtime = timezone.now()
            base.save()
    t = get_template('systack/hotupdate.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))


@csrf_exempt
@login_required(login_url='account_login')
def upload_file(request):
    if request.method == 'POST':
        if handle_uploaded_file(request.FILES['Filedata']):
            return HttpResponse('succees!!')
        else:
            return HttpResponse(404)
    else:
        return HttpResponse(403)

def handle_uploaded_file(file):
    '''上传函数'''
    if file:
        path = os.path.join(settings.MEDIA_ROOT,'upload')
        if not os.path.exists(path):
            os.mkdir(path)
        #ext_name = file.name.split('.')[1]
        #file_name = str(uuid.uuid1())+"."+ext_name
        file_name = file.name
        path_file=os.path.join(path,file_name)
        try:
            with open(path_file,'wb+') as parser:
                for chunk in file.chunks():
                    parser.write(chunk)
        except:
            return False
        return True
    else:
        pass


