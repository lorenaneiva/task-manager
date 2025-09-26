from django.shortcuts import render
from .models import Project, List, Task, ProjectInvitation, ProjectMember
from .forms import ProjectForm, ListForm, TaskForm, ProjectInvitationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

def index(request):
    return render(request, 'task_managers/index.html')


###         projects


@login_required
def projects(request):
    owner_projects = (Project.objects
                      .filter(owner=request.user)
                      .distinct() # evita duplicação
                      .select_related('owner') # otimização de busca da FK
                      .order_by('-date_added')
                      )
    member_projects = (Project.objects
                      .filter(project_members__participants=request.user)
                      .exclude(owner=request.user)
                      .distinct() 
                      .select_related('owner') 
                      .order_by('-date_added')
                      )
    has_member = member_projects.exists()
    context = {'owner_projects':owner_projects,
               'member_projects':member_projects,
               'has_member':has_member
               }
    return render(request, 'task_managers/projects.html',context)

@login_required
def project(request, project_id):
    project = Project.objects.get(id = project_id)
    membership = ProjectMember.objects.filter(project=project,participants=request.user).first()
                            
    is_owner = (request.user == project.owner)
    can_edit = membership.role == 'participant'
    can_invite = is_owner

    lists = project.lists.order_by('-date_added')
    context = {
        'project':project,
        'lists':lists, 
        'can_edit':can_edit,
        'can_invite':can_invite,
        }
    return render(request, 'task_managers/project.html', context)   

@login_required
def new_project(request):
    if request.method != 'POST':
        form = ProjectForm()
    else:
        form = ProjectForm(request.POST) # dados dos campos enviados
        if form.is_valid():
            with transaction.atomic(): # se tiver algum erro as operações anteriores são canceladas
                new_project = form.save(commit=False)
                new_project.owner = request.user 
                new_project.save()
                new_member = ProjectMember.objects.get_or_create(
                    project = new_project,
                    participants=request.user,
                    defaults={'role':'participant'}
                )


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
        messages.error(request,'Projeto deletado com sucesso!')
        return redirect('projects')
    return render(request, 'task_managers/confirm_delete.html', {'project':project})


###         convites


@login_required
def invite(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method != 'POST':
        form = ProjectInvitationForm()
    else:
        form = ProjectInvitationForm(request.POST)
        form.instance.project = project
        form.instance.inviter = request.user
        if form.is_valid():
            form.save()
            messages.success(request,'Usuário convidado com sucesso!')
            return HttpResponseRedirect(reverse('project', args=[project_id]))
    context = {'project':project,'form': form}
    return render(request, 'task_managers/invite.html', context) 

@login_required
def invites_list(request):
    # filtrando os convites pendentes do usario logado
    # traz os dados das FK  
    invites = (ProjectInvitation.objects
               .filter(guest=request.user, status='pending')   # Query
               .select_related('project', 'inviter'))        # otimizando as buscas                         
    context = {'invites':invites}
    return render (request, "task_managers/invites_list.html", context)

@login_required
def invites_accept(request, pk):
    if request.method != "POST":
        return redirect('invites_list')
    else: 
        invite = get_object_or_404(ProjectInvitation, pk=pk, guest=request.user, status='pending')
        # se tiver algum erro as operações anteriores são canceladas
        with transaction.atomic():
            invite.status = 'accepted'
            invite.save(update_fields=['status'])
            # instancia encontrada / boolean 
            member, created = ProjectMember.objects.get_or_create(
                project = invite.project,
                participants=request.user,
                defaults={'role': invite.role}
                )
            if not created and member.role != invite.role:
                member.role = invite.role 
                member.save()
        messages.success(request, "Você entrou no projeto!")
        return redirect("invites_list")

@login_required
def invites_reject(request, pk):
    if request.method != 'POST':
        return redirect('invites_list')
    else:
        invite = get_object_or_404(ProjectInvitation, pk=pk, guest=request.user, status='pending')

        invite.status = 'rejected'
        invite.save(update_fields=['status'])
        messages.info(request, "Convite rejeitado")    
        return redirect('invites_list')   


###         lists


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
        messages.error(request,'Lista deletada com sucesso!')
        return redirect('project', project_id=project_id)
    return render(request, 'task_managers/confirm_delete.html', {'list':list})



###         tasks



@login_required
def task(request, project_id, task_id):
    task = get_object_or_404(Task, id=task_id)
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
def edit_task(request, project_id, task_id):
    task = get_object_or_404(Task, id=task_id)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, 'Tarefa atualizada com sucesso')
        return redirect('task', project_id=project_id, task_id=task_id)

    return render(request, 'task_managers/edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id, project_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        messages.error(request,'Tarefa deletada com sucesso!')
        return redirect('project', project_id=project_id)
    return render(request, 'task_managers/confirm_delete.html', {'task':task})

