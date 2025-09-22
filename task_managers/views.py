from django.shortcuts import render
from .models import Project, List,Task
from .forms import ProjectForm, ListForm, TaskForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    return render(request, 'task_managers/index.html')

@login_required
def projects(request):
    projects = Project.objects.filter(owner=request.user).order_by('date_added')
    context = {'projects':projects}
    return render(request, 'task_managers/projects.html',context)

@login_required
def project (request, project_id):
    project = Project.objects.get(id = project_id)
    lists = project.lists.order_by('-date_added')
    context = {'project':project,'lists':lists}
    return render(request, 'task_managers/project.html', context)   

@login_required
def new_project(request):
    if request.method != 'POST':
        form = ProjectForm()
    else:
        form = ProjectForm(request.POST) # dados dos campos enviados
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.owner = request.user 
            new_project.save()
            messages.success(request,'Projeto criado com sucesso!')
            return HttpResponseRedirect(reverse('projects'))
        
    context = {'form': form}
    return render(request, 'task_managers/new_project.html', context)

@login_required
def edit_project (request, project_id):
    project = get_object_or_404(Project, pk=project_id) #pk = primary key

    form = ProjectForm(request.POST or None, instance=project) 
    if form.is_valid():
        form.save()
        messages.success(request,'Projeto atualizado com sucesso!')
        return HttpResponseRedirect(reverse('projects'))     
      
    context = {'form':form, 'project':project}
    return render(request, 'task_managers/edit_project.html',context) 

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        project.delete()
        messages.success(request,'Projeto deletado com sucesso!')
        return redirect('projects')
    return render(request, 'task_managers/confirm_delete.html', {'project':project})

@login_required
def new_list(request, project_id):
    project = Project.objects.get(id = project_id)
    if request.method != 'POST':
        form = ListForm()
    else:
        form = ListForm(request.POST, instance=List(project=project)) # instance para evitar erro
        if form.is_valid():
            form.save()
            messages.success(request,'Lista criada com sucesso!')
            return HttpResponseRedirect(reverse('project', args=[project_id]))
        
    context = {'project': project,'form': form}
    return render(request, 'task_managers/new_list.html', context)

@login_required
def edit_list(request, list_id):
    list = get_object_or_404(List, pk=list_id)
    form = ListForm(request.POST or None, instance=list)
    if form.is_valid():
        form.save()
        messages.success(request,'Lista atualizada com sucesso!')
        return HttpResponseRedirect(reverse('project', args=[list.project.id]))     
    
    context = {'form':form, 'list':list}
    return render(request, 'task_managers/edit_list.html',context)   

@login_required
def delete_list(request, project_id, list_id):
    list = get_object_or_404(List, id=list_id)

    if request.method == 'POST':
        list.delete()
        messages.success(request,'Lista deletada com sucesso!')
        return redirect('project', project_id=project_id)
    return render(request, 'task_managers/confirm_delete.html', {'list':list})

@login_required
def task(request, project_id, task_id):
    task = Task.objects.get(id = task_id)
    context = {'task': task}
    return render(request, 'task_managers/task.html', context)

@login_required
def new_task(request, list_id):
    list = List.objects.get(id = list_id)
    if request.method != 'POST':
        form = TaskForm()
    else:
        form = TaskForm(request.POST, instance=Task(list=list))
        if form.is_valid():
            form.save()
            messages.success(request,'Tarefa criada com sucesso!')
            return HttpResponseRedirect(reverse('project', args=[list.project_id]))
        
    context = {'list': list,'form': form}
    return render(request, 'task_managers/new_task.html', context)

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.sucess(request, 'Tarefa atualizada com sucesso')
        return HttpResponseRedirect(reverse('projects'))    
    context = {'form':form, 'task':task}
    return render(request,'task_managers/edit_task.html', context) 

@login_required
def delete_task(request, task_id, project_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        messages.success(request,'Tarefa deletada com sucesso!')
        return redirect('project', project_id=project_id)
    return render(request, 'task_managers/confirm_delete.html', {'task':task})

