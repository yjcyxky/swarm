from django.contrib import admin
from sscluster import models

admin.site.register(models.ToDoList)
admin.site.register(models.Cluster)
admin.site.register(models.JobLog)
