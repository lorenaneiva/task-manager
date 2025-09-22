from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from datetime import date 
from django.conf import settings


def validate_deadline(value):
    if value < date.today():
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
    deadline = models.DateField(blank=True, null=True, validators=[validate_deadline])

    def __str__(self):
        return self.title
    
    def clean(self):
        if  (self.deadline) and (self.list.project.deadline):    
            if  self.deadline > self.list.project.deadline:
                raise ValidationError("O prazo da tarefa não pode passar do prazo do projeto.")

        if  (self.deadline) and (self.list.deadline):
                if self.deadline > self.list.deadline:
                    raise ValidationError("O prazo da tarefa não pode passar do prazo da lista")    