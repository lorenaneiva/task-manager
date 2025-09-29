from django import forms
from .models import Project, List, Task, ProjectInvitation
from django.contrib.auth.models import User

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

    guest_username = forms.CharField(label="convidado", max_length=150)

    class Meta():
        model = ProjectInvitation
        fields = ['guest_username','role']
        labels = {'role':'tipo de participação'}

    # form.is_valid()
    def clean(self):
        cleaned = super().clean() # validação padrão do django
        username = cleaned.get("guest_username", "").strip() # valor digitado no campo

        if not username:
            raise forms.ValidationError("Digite o username do convidado")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Usuário não encontrado")
        self.instance.guest = user

        return cleaned
    