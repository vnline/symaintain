#!-*- coding=utf-8 -*-
#from django.utils import timezone
import sys,os
import redis
import Common
from django.db import models
from mc_salt.master.lib import utils,client


# Create your models here.

class Schedule(models.Model):
    agent = models.CharField(max_length=20)
    server_name = models.CharField(max_length=20)
    open_time = models.DateTimeField(auto_now = False)
    version = models.CharField(max_length=50)
    deploy = models.BooleanField()
    created_by = models.CharField(max_length=20,blank=True)
    deployed_by = models.CharField(max_length=20)
    status = models.BooleanField()
    remark = models.TextField(max_length=200,blank=True)
    mtime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.server_name
    class Meta:
        db_table = "schedule"


class Deliver(models.Model):
    target = models.CharField(max_length=20)
    files = models.TextField(max_length=200)
    jids = models.TextField(max_length=200, blank=True)
    result = models.TextField(max_length=500, blank=True)
    deployed_by = models.CharField(max_length=20,blank = True)
    mtime = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = "deliver"

    def __unicode__(self):
        return self.files

class Hotfile(models.Model):
    target = models.CharField(max_length=20)
    files = models.TextField(max_length=200)
    jids = models.TextField(max_length=200, blank=True)
    result = models.TextField(max_length=500, blank=True)
    deployed_by = models.CharField(max_length=20,blank = True)
    mtime = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = "hotfile"

    def __unicode__(self):
        return self.files

class Deploy(models.Model):
    target = models.CharField(max_length=20)
    open_time = models.DateTimeField(auto_now = False)
    deploy_name = models.CharField(max_length=20)
    prev_name = models.CharField(max_length=20)
    importdb = models.BooleanField()
    cgm = models.BooleanField()
    deployed_by = models.CharField(max_length=20)
    jids = models.TextField(max_length=200, blank=True)
    result = models.TextField(max_length=500, blank=True)
    mtime = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = "deploy"

    def __unicode__(self):
        return self.deploy_name


class Operation(models.Model):
    target = models.CharField(max_length=20)
    cmd = models.CharField(max_length=200)
    deployed_by = models.CharField(max_length=20)
    jids = models.TextField(max_length=200, blank=True)
    result = models.TextField(max_length=200, blank=True)
    mtime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.cmd
    class Meta:
        db_table = "operation"