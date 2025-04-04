from django.contrib import admin
from job.models import JobApplication, JobPosition

admin.site.register(JobApplication)
admin.site.register(JobPosition)