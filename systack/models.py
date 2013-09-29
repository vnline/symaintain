from django.utils import timezone
from django.db import models
import os

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

class Hot_update(models.Model):
    target = models.CharField(max_length=20)
    files = models.FileField(upload_to ='hotupdate/%Y/%m/',blank = True)
    hot_status = models.BooleanField()
    deployed_by = models.CharField(max_length=20)
    mtime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.files

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        db_table = "hot_update"

class Deploy(models.Model):
    target = models.CharField(max_length=20)
    open_time = models.DateTimeField(auto_now = False)
    deploy_name = models.CharField(max_length=20)
    prev_name = models.CharField(max_length=20)
    importdb = models.BooleanField()
    add_pay = models.BooleanField()
    cgm = models.BooleanField()

    class Meta:
        db_table = "deploy"

class Operation(models.Model):
    target = models.CharField(max_length=20)
    cmd = models.CharField(max_length=200)
    sd_name = models.CharField(max_length=20)
    mtime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.cmd
    class Meta:
        db_table = "operation"