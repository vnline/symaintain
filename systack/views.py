#!-*- coding=utf-8 -*-

import os
import json
from models import *
from form import *
from Common import *
from django.template import RequestContext
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
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseServerError,HttpResponseNotAllowed,HttpResponseNotFound,Http404


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
    try:
        schedules = Schedule.objects.get(id=itemid)
        schedules.delete()
        return HttpResponseRedirect(reverse('schedule'))
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('error'))

@login_required(login_url='account_login')
def finish(request,itemid):
    try:
        schedule_instance = Schedule.objects.get(id=itemid)
        schedule_instance.deployed_by = unicode(request.user)
        schedule_instance.deploy = True
        if schedule_instance.open_time < timezone.now():
            schedule_instance.status = 'True'
        schedule_instance.save()
        return HttpResponseRedirect(reverse('schedule'))
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('error'))

@login_required(login_url='account_login')
def error(request):
    t = get_template('systack/404.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@login_required(login_url='account_login')
def deploy(request):
    if request.method == 'POST':
        deploy = Deploy()
        form = DeployForm(request.POST,instance=deploy)
        if form.is_valid():
            base = form.save(commit=False)
            base.deployed_by = unicode(request.user)
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
def deliver(request):
    if request.method == 'POST':
        deliver = Deliver()
        form = DeliverForm(request.POST,instance=deliver)
        if form.is_valid():
            deliver = form.save(commit=False)
            target = request.POST.get('target')
            files = request.POST['files'].split('\r\n')
            deliver.files = Common.get_file_name(files)
            deliver.jids = Common.deliver(target,files)
            deliver.deployed_by = unicode(request.user)
            deliver.mtime = timezone.now()
            deliver.save()
    delivers = Deliver.objects.all().order_by('-id')
    paginator = Paginator(delivers, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        delivers = paginator.page(page)
    except :
        delivers = paginator.page(paginator.num_pages)
    t = get_template('systack/deliver.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))


@login_required(login_url='account_login')
def hotfile(request):
    if request.method == 'POST' or request.is_ajax():
        hotfile = Hotfile()
        form = HotfileForm(request.POST,instance=hotfile)
        if form.is_valid():
            hot = form.save(commit=False)
            target = request.POST.get('target')
            files = request.POST['files'].split('\r\n')
            hot.files = Common.get_file_name(files)
            hot.jids = Common.hot_files(target,files)
            hot.deployed_by = unicode(request.user)
            hot.mtime = timezone.now()
            hot.save()
    hot = Hotfile.objects.all().order_by('-id')
    paginator = Paginator(hot, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        hot = paginator.page(page)
    except :
        hot = paginator.page(paginator.num_pages)
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
            return HttpResponseNotFound()
    else:
        return HttpResponseNotAllowed('GET')

def handle_uploaded_file(file):
    """
    文件上传处理函数
    """
    if file:
        path = os.path.join(settings.MEDIA_ROOT,'upload')
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except:
                return False
        file_name = file.name
        file_path = os.path.join(path,file_name)
        try:
            with open(file_path,'wb+') as parser:
                for chunk in file.chunks():
                    parser.write(chunk)
        except:
            return False
        return True
    else:
        return HttpResponseServerError()


@login_required(login_url='account_login')
def get_log(request):
    try:
        if request.GET.has_key('conf_jids'):
            lst_update_jid = request.GET['conf_jids'].split(',')
        else:
            lst_update_jid = request.GET['jid'].split(',')
        print(lst_update_jid)
        queue_id = request.GET['queue_id']
        rds = RdsTool(queue_id)
        q_result = rds.rds_read_all()
        result_dict = {}
        tmp = {}
        for q_id in q_result:
            for jid in lst_update_jid:
                ret_dict = Get_log.get_job_result(jid,q_id)
                if ret_dict:
                    if type(ret_dict['return']) == type({}):
                        node_id = ret_dict['node_id']
                        file_name = os.path.basename(ret_dict['return'].keys()[0])
                        file_ret =  ret_dict['return'].values()[0]
                        tmp.update({file_name:file_ret})
                        result_dict.update({node_id:tmp})
                    elif type(ret_dict['return']) == type(0):
                        node_id = ret_dict['node_id']
                        result_dict[node_id] = ret_dict['return']
                else:
                    pass
        return HttpResponse(json.dumps(result_dict))
    except:
        raise Http404

@csrf_exempt
def ajax_test(request):
    #if request.is_ajax():
    #    if request.method == 'GET':
    #        message = "This is an XHR GET request"
    #    elif request.method == 'POST':
    #        message = "This is an XHR POST request"
    #        # Here we can access the POST data
    #        print request.POST
    #else:
    #    message = "No XHR"
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['Email']
        sug = request.POST['sug']
        return HttpResponse(name)
    else:
        jids = request.GET['jids']
        print list(jids)
        return HttpResponse(jids)

def test(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['files'])
            #print request.FILES
            HttpResponse('succees!!')
    else:
        form = UploadFileForm()
    t = get_template('systack/upload.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))




