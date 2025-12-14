from django import forms
from src.models.projects import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "client", "description", "start_date", "deadline", "budget", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Project Name"}),
            "client": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "description": forms.Textarea(attrs={"class": "textarea textarea-bordered w-full", "rows": 4, "placeholder": "Project Description"}),
            "start_date": forms.DateInput(attrs={"class": "input input-bordered w-full", "type": "date"}),
            "deadline": forms.DateInput(attrs={"class": "input input-bordered w-full", "type": "date"}),
            "budget": forms.NumberInput(attrs={"class": "input input-bordered w-full", "placeholder": "0.00"}),
            "status": forms.Select(attrs={"class": "select select-bordered w-full"}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input input-bordered w-full input-sm", "placeholder": "Task Title"}),
            "description": forms.Textarea(attrs={"class": "textarea textarea-bordered w-full textarea-sm", "rows": 2, "placeholder": "Task Description"}),
            "status": forms.Select(attrs={"class": "select select-bordered w-full select-sm"}),
            "due_date": forms.DateInput(attrs={"class": "input input-bordered w-full input-sm", "type": "date"}),
        }
