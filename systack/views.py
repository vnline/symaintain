#!-*- coding=utf-8 -*-

import os
#import json
from models import *
from form import *
from Common import *
#from django.core import serializers
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.messages import api as messages,constants as message
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from symaintain import settings
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseServerError,HttpResponseNotAllowed,HttpResponseNotFound,Http404


@login_required(login_url='account_login')
def index(request):
    '''首页'''

    if request.user.is_authenticated():
        user = request.user
        #return render_to_response('index.html',{'user':user},context_instance=RequestContext(request))
        plan_s = Schedule.objects.all()
        plan_sum = plan_s.count()
        start_s = Schedule.objects.filter(status__exact=1)
        start_sum = start_s.count()
        deployed = Schedule.objects.filter(deploy__exact=1)
        deployed_sum = deployed.count()
        hots = Hotfile.objects.all()
        hots_sum = hots.count()
        delivers = Deliver.objects.all()
        delivers_sum = delivers.count()
        rds = RdsTool()
        node_sum = len(rds.rds_read_all())
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
            if validate_login(request, form.cleaned_data["username"], form.cleaned_data["password"]):
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponseRedirect(reverse('account_login'))
    #template_var["form"] = form
    #return render_to_response('login.html', template_var, context_instance=RequestContext(request))
    t = get_template('systack/login.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@login_required(login_url='account_login')
def register(request):
    '''用户注册页'''
    template_var = {}
    form = LoginForm()
    if request.method == "POST":
        form = RegisterForm(request.POST.copy())
        if form.is_valid():
            validate_login(request, form.cleaned_data["username"], form.cleaned_data["password"])
            return HttpResponseRedirect(reverse('index'))
    template_var["form"] = form
    #return render_to_response('login.html', template_var, context_instance=RequestContext(request))
    t = get_template('systack/register.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@staff_member_required
@login_required(login_url='account_login')
def manager(request):
    '''用户管理页'''
    users = User.objects.all().values()
    paginator = Paginator(users ,5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        page = paginator.page(page)
    except :
        page = paginator.page(paginator.num_pages)
    t = get_template('systack/user_manager.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@staff_member_required
@login_required(login_url='account_login')
def user_edit(request,uid):
    '''用户管理页'''
    tmptag = True
    users = User.objects.get(id=uid)
    if request.method == 'POST':
        users.email = request.POST.get('email')
        oldpassword = request.POST.get('pre_password')
        newpassword = request.POST.get('password')
        repassword = request.POST.get('repassword')
        user = authenticate(username=users.username,password=oldpassword)
        if user:
            if newpassword is not None:
                if newpassword == repassword:
                    user.set_password(newpassword)
                else:
                    messages.add_message(request, message.INFO, _(u'两次输入的密码不一致'))
                    tmptag = False
            if request.POST.get('is_staff') == "on":
                users.is_staff = True
            else:
                users.is_staff = False
            if request.POST.get('is_active') == "on":
                users.is_active = True
            else:
                users.is_active = False
            users.save()
            if tmptag:
                return HttpResponseRedirect(reverse('manager'))
            else:
                pass
    t = get_template('systack/user_edit.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@staff_member_required
@login_required(login_url='account_login')
def delete_user(request,itemid):
    try:
        user = User.objects.get(id=itemid)
        user.delete()
        return HttpResponseRedirect(reverse('manager'))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('error'))

def logout(request):
    '''用户注销页'''
    auth_logout(request)
    return HttpResponseRedirect(reverse('account_login'))

#@permission_required('systack.schedule.can_add',login_url='/error')
@login_required(login_url='account_login')
def schedule(request):
    if request.method == 'POST':
        schedule = Schedule()
        form = ScheduleForm(request.POST,instance=schedule)
        if form.is_valid():
            base = form.save(commit=False)
            base.created_by = unicode(request.user)
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
    t = get_template('404.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@staff_member_required
#@permission_required('systack.Deploy.can_add',login_url='/error')
@login_required(login_url='account_login')
def deploy(request):
    if request.method == 'POST':
        deploy = Deploy()
        form = DeployForm(request.POST,instance=deploy)
        if form.is_valid():
            base = form.save(commit=False)
            base.deployed_by = unicode(request.user)
            base.mtime = timezone.now()
            target = request.POST.get('target')
            deploy_name = request.POST.get('deploy_name')
            prev_name = request.POST.get('prev_name')
            online_date,online_time = request.POST.get('open_time').split(' ')
            importdb = request.POST.get('importdb')
            cgm = request.POST.get('cgm')
            base.jids = Common.deploy(target,online_date, online_time, deploy_name, prev_name, importdb=importdb, cgm=cgm)
            base.save()
    deploys = Deploy.objects.all().order_by('-id')
    paginator = Paginator(deploys ,5)
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

@staff_member_required
#@permission_required('systack.Deliver.can_add',login_url='/error')
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

@staff_member_required
#@permission_required('systack.Operation.can_add',login_url='/error')
@login_required(login_url='account_login')
def operation(request):
    t = get_template('systack/operation.html')
    c = RequestContext(request,locals())
    if request.method == 'POST':
        as_role = request.POST.get('as_role' or None)
        target = request.POST.get('target' or None)
        cmd = request.POST.get('cmd' or None)
        arg = request.POST.get('arg' or None)
        jids = Common.command(as_role,target,cmd,arg)
        return HttpResponse(jids)
    return HttpResponse(t.render(c))

@staff_member_required
#@permission_required('systack.Hotfile.can_add',login_url='/error')
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

@csrf_exempt
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

@csrf_exempt
@login_required(login_url='account_login')
def get_log(request):
    role = request.GET['role']
    lst_update_jid = request.GET['conf_jids'].split(',')
    if role == "main":
        q_result = Common.get_hosts()
        print q_result
    else:
        rds = RdsTool()
        q_result = rds.rds_read_all()
    rdl = RdsLog(db='1')
    result_dict = {}
    data = {
        'role':[],
        'main_id':[],
        'node_id':[],
        'msg':[],
        'result':[]
    }
    for q_id in q_result:
        for jid in lst_update_jid:
            ret_dict = rdl.get_job_result(jid,q_id)
            if ret_dict:
                print ret_dict
                if type(ret_dict['return']) == type({}):
                    role = ret_dict['role']
                    main_id = ret_dict['main_id']
                    node_id = ret_dict['node_id']
                    try:
                        file_name = os.path.basename(ret_dict['return'].keys()[0])
                        file_ret =  ret_dict['return'].values()[0]
                    except:
                        file_name = ""
                        file_ret = ""
                    data['role'].append(role)
                    data['main_id'].append(main_id)
                    data['node_id'].append(node_id)
                    data['msg'].append(file_name)
                    data['result'].append(file_ret)
                    result_dict.update(data)
                elif type(ret_dict['return']) == type(0) or ret_dict['return'] == "":
                    role = ret_dict['role']
                    main_id = ret_dict['main_id']
                    node_id = ret_dict['node_id']
                    msg = ""
                    result = str(ret_dict['return'])
                    data['role'].append(role)
                    data['main_id'].append(main_id)
                    data['node_id'].append(node_id)
                    data['msg'].append(msg)
                    data['result'].append(result)
                    result_dict.update(data)
                else:
                    continue
    try:
        print result_dict
        list = zip(result_dict['role'],result_dict['main_id'],result_dict['node_id'],result_dict['msg'],result_dict['result'])
    except Exception:
        list = [('None','None','None',False)]
    t = get_template('systack/modal.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

@csrf_exempt
@login_required(login_url='account_login')
def game_log(request):
    ret = {}
    try:
        if request.GET.has_key('deploy'):
            jid = request.GET.get('deploy')
            id = ""
            ret = Get_log.get_job_result(jid,id,key='init_game')
            ret_list = ret.split('#')
    except:
        pass
    t = get_template('systack/modal.html')
    c = RequestContext(request,locals())
    return HttpResponse(t.render(c))

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




