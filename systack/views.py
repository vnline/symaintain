#!-*- coding=utf-8 -*-

import os
from models import *
from form import *
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
from mc_salt.master.lib import client
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseServerError,HttpResponseNotAllowed,HttpResponseNotFound


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
    t = get_template('systack/error.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@login_required(login_url='account_login')
def deploy(request):
    if request.method == 'POST':
        deploy = Deploy()
        form = DeployForm(request.POST,instance=deploy)
        if form.is_valid():
            base = form.save(commit=False)
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
    if request.method == 'POST':
        hots = Hot_update()
        form = Hot_updateForm(request.POST,instance=hots)
        if form.is_valid():
            hotfile = form.save(commit=False)
            target = request.POST.get('target')
            files = request.POST['files'].split(' ')
            hotfile.files = hots.get_file_name(files)
            result_dict =  hots.file_update(target,files)
            hotfile.result = result_dict
            hotfile.deployed_by = unicode(request.user)
            hotfile.mtime = timezone.now()
            hotfile.save()
    hots = Hot_update.objects.all().order_by('-id')
    paginator = Paginator(hots ,5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        hots = paginator.page(page)
    except :
        hots = paginator.page(paginator.num_pages)
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

def copy_update(target,files):
    """
    文件热更函数
    """
    send_ret = {}
    hot_ret = {}
    result_dict = {}
    cli = client.Client("%s" % target ,role="node",timeout=120)
    for file in files:
        file = file.encode('utf-8')
        file_name = os.path.basename(file)
        mod,file_ext = os.path.splitext(file_name)
        file_path = '/data/web/systack/media/upload'+ file_name
        if not os.path.exists(file_path):
            return False
        send_ret[file_name] = cli.node_sys.node_copy(file_path,file)
        if file_ext == ".beam":
            hot_ret[file_name]  = cli.gstools.node_hot('hot_update',mod)
        else:
            pass
    for k,v in send_ret.iteritems():
        result_dict.setdefault(k,[ ]).append(v)
    for k,v in hot_ret.items():
        result_dict.setdefault(k,[ ]).append(v)
    print "I'm HERE!!!"
    return result_dict

@login_required(login_url='account_login')
def get_log(request):
    try:
        if request.GET.has_key('conf_jids'):
            lst_update_jid = request.GET['conf_jids'].split(',')
        else:
            lst_update_jid = request.GET['jid'].split(',')
        queue_id = request.GET['queue_id']
        rds = RdsTool(queue_id)
        q_result = rds.rds_read_all()
        int_suc = 0
        int_fail = 0
        int_sum = len(q_result)
        result_dict = {}
        for q_id in q_result:
            result_dict[q_id] = 0
            for jid in lst_update_jid:
                ret_dict = Deploy.get_job_result(jid,q_id)
                if type(ret_dict['return']) == type({}):
                    for _,v in ret_dict['return'].items():
                        if v == False or v == 0:
                            break
                        else:
                            result_dict[q_id] += 1
                elif type(ret_dict['return']) == type(0):
                    if ret_dict['return'] == True or ret_dict['return'] == 1:
                        result_dict[q_id] += 1
                    else:
                        break
        for k,v in result_dict.items():
            if v < len(lst_update_jid):
                int_fail += 1
                result_dict[k] = 0
            elif v == 0:
                result_dict[k] = -1
            else:
                result_dict[k] = 1
                int_suc += 1
    except:
        return HttpResponseNotFound()




