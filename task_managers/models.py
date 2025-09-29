from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from datetime import date 
from django.conf import settings


def validate_deadline(value):
    if value and value < date.today():
        raise ValidationError("Não é possível selecionar uma data passada.")

class Project(models.Model):
    STATUS_CHOICES=[
    ("to-do", "A fazer"),
    ("doing", "Fazendo"),
    ("done", "Feito"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="to-do"
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True, validators=[validate_deadline])
    
    def __str__(self):
        return self.title
    def clean(self):
        if self.deadline and self.deadline < date.today():
            raise ValidationError("Não é possível selecionar uma data passada.")

# model intermediario N:N

class ProjectMember(models.Model): 
    # projeto 
    project = models.ForeignKey(Project, on_delete=models.CASCADE,related_name='project_members') 
    # todos os participantes (incluindo o dono) 
    participants = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_participants') 
    accepted_at = models.DateTimeField(auto_now_add=True) 
    # tipo de participante 
    ROLE_CHOICES = [ 
        ('viewer', 'visualizador'), 
        ('participant', 'participante'), 
        ] 
    
    role = models.CharField( max_length=20, choices=ROLE_CHOICES, default='participant' )

    class Meta: # validação para que a combinação dos campos seja unica 
        constraints = [ 
            models.UniqueConstraint( 
                fields=['project','participants'], name='unique_project_participants' 
                ) ] 
        
    def __str__(self): 
        return self.participants.username   

class List(models.Model):
    STATUS_CHOICES=[
    ("to-do", "A fazer"),
    ("doing", "Fazendo"),
    ("done", "Feito"),
    ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="to-do"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="lists")
    title = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True, validators=[validate_deadline])

    def __str__(self):
        return self.title
    def clean(self):
        if (self.deadline) and (self.project.deadline):    
            if self.deadline > self.project.deadline:
                raise ValidationError("O prazo da lista não pode passar do prazo do projeto.")
        if self.deadline and self.deadline < date.today():
            raise ValidationError("Não é possível selecionar uma data passada.")

class Task(models.Model):
    STATUS_CHOICES=[
        ("to-do", "A fazer"),
        ("doing", "Fazendo"),
        ("done", "Feito"),
        ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="to-do"
    )
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    # prazo da tarefa
    deadline = models.DateField(blank=True, null=True, validators=[validate_deadline])
    # responsavel atribuido a tarefa (opicional) 
    assigned = models.ForeignKey(ProjectMember, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_tasks')

    def __str__(self):
        return self.title
    
    def clean(self):
        if  (self.deadline) and (self.list.project.deadline):    
            if  self.deadline > self.list.project.deadline:
                raise ValidationError("O prazo da tarefa não pode passar do prazo do projeto.")

        if  (self.deadline) and (self.list.deadline):
                if self.deadline > self.list.deadline:
                    raise ValidationError("O prazo da tarefa não pode passar do prazo da lista")    
                
        # validação para coerencia 
        if (self.assigned): 
            if self.assigned.project != self.list.project: 
                raise ValidationError("O projeto da tarefa deve ser o mesmo projeto do responsável.")
            
        if self.deadline and self.deadline < date.today():
            raise ValidationError("Não é possível selecionar uma data passada.")

class ProjectInvitation(models.Model): 
    # projeto 
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='invitations') 
    
    # dono do projeto 
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='invitations_sent') 
    
    # convidado para o projeto 
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='invitations_received') 
    # status do convite 

    INVITATION_CHOICES = [ 
        ('pending','Pendente'), 
        ('accepted','Aceito'), 
        ('rejected','Rejeitado') 
        ] 
    status = models.CharField( 
        max_length=20, 
        choices=INVITATION_CHOICES, 
        default='pending' ) 
    
    ROLE_CHOICES = [ 
        ('viewer', 'visualizador'), 
        ('participant', 'participante'), 
        ] 
    
    role = models.CharField( 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='participant' )
    
    def clean(self):
        # Regra do dono: só valida se project e inviter já existem
        if self.project_id and self.inviter_id:
            if self.inviter != self.project.owner:
                raise ValidationError("Apenas o dono do projeto pode convidar.")

        # Não pode convidar a si mesmo (só se ambos existem)
        if self.inviter_id and self.guest_id and self.inviter_id == self.guest_id:
            raise ValidationError("Você não pode enviar o convite para si mesmo.")

        # Regras que dependem de project E guest – só rodam se ambos existem
        if self.project_id and self.guest_id:
            is_member = ProjectMember.objects.filter(
                project_id=self.project_id,
                participants_id=self.guest_id,
            ).exists()
            if is_member:
                raise ValidationError("Usuário já é membro deste projeto.")

            if self.status == "pending":
                qs = ProjectInvitation.objects.filter(
                    project_id=self.project_id,
                    guest_id=self.guest_id,
                    status="pending",
                )
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError("Já existe um convite pendente para este usuário.")

    def __str__(self):
        # Evita acessar a relação quando ainda não foi definida
        nome = self.guest.username if self.guest_id else "(sem convidado)"
        return f"Convite para {nome}"