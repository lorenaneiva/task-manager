from django.contrib import admin
from task_managers.models import (Project,List,Task ) 
from django.urls import reverse
from django.utils.html import format_html

class ProjectAdmin(admin.ModelAdmin):
    list_display=["title","date_added","deadline"]
    search_fields=["title"]

admin.site.register(Project, ProjectAdmin)

class ListAdmin(admin.ModelAdmin):
    list_display=["title","project","date_added","deadline"]
    search_fields=["title"]

admin.site.register(List, ListAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display=["title","list","date_added","deadline"]
    search_fields=["title"]

admin.site.register(Task, TaskAdmin)