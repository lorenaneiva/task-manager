from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    #home
    path('', views.index, name='index'),

    #projects
    path('projects', views.projects, name='projects'), 
    path('projects/<int:project_id>', views.project, name='project'), 
    path('newproject', views.new_project, name='new_project'), 
    path('projects/edit/<int:project_id>', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete', views.delete_project, name='delete_project'), 
    # invites
    path('projects/<int:project_id>/invite', views.invite, name='invite'), 
    path('projects/invites/', views.invites_list, name='invites_list'), 
    path('projects/<int:pk>/accept', views.invites_accept, name='invites_accept'), 
    path('projects/<int:pk>/reject', views.invites_reject, name='invites_reject'), 
    

    #taskslists
    path('newlist/<int:project_id>', views.new_list, name='new_list'), 
    path('list/edit/<int:list_id>',views.edit_list, name='edit_list'),
    path('projects/<int:project_id>/lists/<int:list_id>/delete', views.delete_list, name='delete_list'), 

    #tasks
    path('projects/<int:project_id>/<int:task_id>', views.task, name='task'), 
    path('newtask/<int:list_id>', views.new_task, name='new_task'), 
    path('task/edit/<int:project_id>/<int:task_id>', views.edit_task, name='edit_task'), 
    path('projects/<int:project_id>/tasks/<int:task_id>/delete', views.delete_task, name='delete_task'), 

    #sobre a aplicação
    path('sobre/', TemplateView.as_view(template_name='task_managers/sobre.html'), name='sobre'),

]