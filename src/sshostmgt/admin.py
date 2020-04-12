from django.contrib import admin
from sshostmgt import models

admin.site.register(models.IPMI)
admin.site.register(models.BIOS)
admin.site.register(models.RAID)
admin.site.register(models.System)
admin.site.register(models.Tag)
admin.site.register(models.Host)
admin.site.register(models.CPU)
admin.site.register(models.Network)
admin.site.register(models.Storage)
admin.site.register(models.Memory)
