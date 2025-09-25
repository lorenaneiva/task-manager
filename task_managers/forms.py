from django import forms
from .models import Project, List, Task, ProjectInvitation

class ProjectForm(forms.ModelForm):
    deadline = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d'), #formato no HTML
        input_formats=['%Y-%m-%d'], #formato que o forms aceita
        label='Prazo') 
    
    class Meta():
        model = Project
        fields = ['title', 'status', 'deadline']
        labels = {'title': 'Nome', 'status': 'Status'}

class ListForm(forms.ModelForm):
    deadline = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='Prazo')
    
    class Meta():
        model = List
        fields = ['title', 'status', 'deadline']
        labels = {'title': 'Nome', 'status': 'Status'}

class TaskForm(forms.ModelForm):
    deadline = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='Prazo')
    
    class Meta():
        model = Task
        fields = ['title', 'status', 'deadline', 'assigned', 'description',]
        labels = {'title': 'Nome', 'status': 'Status'}

class ProjectInvitationForm(forms.ModelForm):
    class Meta():
        model = ProjectInvitation
        fields = ['guest','role']
    #construtor, lista de argumentos, dicionario com argumentos
    def __init__(self, *args, **kwargs): 
        project = kwargs.pop('project', None) # retirando a chave do dic.
        # constr. da classe mae, criando os campos para acessa-los
        super().__init__(*args, **kwargs) 
        if project:
            # filtrando o que aparece no campo
            self.fields['assigned'].queryset = project.project_participants.all()