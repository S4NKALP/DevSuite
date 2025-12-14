from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
from src.models.projects import Project, Task
from src.api.projects.forms import ProjectForm, TaskForm

def project_list(request):
    projects = Project.objects.all().select_related('client')
    return render(request, 'projects/project_list.html', {'projects': projects})

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

def get_kanban_context(project):
    tasks = project.tasks.all()
    return {
        'project': project,
        'tasks_todo': tasks.filter(status='TODO'),
        'tasks_in_progress': tasks.filter(status='IN_PROGRESS'),
        'tasks_review': tasks.filter(status='REVIEW'),
        'tasks_done': tasks.filter(status='DONE'),
    }

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    context = get_kanban_context(project)
    # Add a blank task form for the "Add Task" modal/section
    context['task_form'] = TaskForm()
    return render(request, 'projects/project_detail.html', context)

@require_http_methods(["POST"])
def task_create(request, project_id):
    import logging
    from datetime import datetime
    logger = logging.getLogger(__name__)
    
    logger.info(f"Task create called for project {project_id}")
    logger.info(f"POST data: {request.POST}")
    
    project = get_object_or_404(Project, pk=project_id)
    title = request.POST.get('title', '').strip()
    status = request.POST.get('status', 'TODO')
    due_date_str = request.POST.get('due_date', '').strip()
    
    # Parse due_date string to date object
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid due_date format: {due_date_str}")
    
    logger.info(f"Title: '{title}', Status: '{status}', Due Date: '{due_date}'")
    
    if not title:
        logger.error("Task title is empty")
        return HttpResponse("Task title is required", status=400)
    
    try:
        task = Task.objects.create(
            project=project,
            title=title,
            status=status,
            due_date=due_date
        )
        logger.info(f"Task created successfully: {task.id}")
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return HttpResponse(f"Error creating task: {str(e)}", status=500)
    
    # Return the task HTML directly
    due_date_html = ''
    if task.due_date:
        due_date_html = f'''
                        <div class="text-xs text-base-content/60 mt-1 flex items-center gap-1">
                            <span class="icon-[tabler--calendar] size-3"></span>
                            {task.due_date.strftime("%b %d")}
                        </div>'''
    
    html = f'''<div class="task-item card bg-base-100 shadow-sm hover:shadow-md p-3 cursor-move" 
         draggable="true" 
         data-task-id="{task.id}"
         id="task-{task.id}">
        <div class="flex items-start justify-between gap-2">
            <div class="flex-1">
                <p class="text-sm font-medium">{task.title}</p>{due_date_html}
            </div>
            <div class="dropdown dropdown-end">
                <div tabindex="0" role="button" class="btn btn-ghost btn-xs btn-square">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                </div>
                <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-32">
                    <li><a class="edit-task-btn" data-task-id="{task.id}">Edit</a></li>
                    <li><a class="delete-task-btn" data-task-id="{task.id}">Delete</a></li>
                </ul>
            </div>
        </div>
    </div>'''
    
    logger.info(f"Returning HTML response (length: {len(html)})")
    return HttpResponse(html)

@require_http_methods(["POST"])
def task_update_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    status = request.POST.get('status')
    if status in dict(Task.STATUS_CHOICES):
        task.status = status
        task.save()
    
    project = task.project
    context = get_kanban_context(project)
    return render(request, 'projects/partials/kanban_board.html', context)

@require_http_methods(["POST"])
def task_edit(request, task_id):
    import logging
    from datetime import datetime
    logger = logging.getLogger(__name__)
    
    task = get_object_or_404(Task, pk=task_id)
    title = request.POST.get('title', '').strip()
    due_date_str = request.POST.get('due_date', '').strip()
    
    # Parse due_date string to date object
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid due_date format: {due_date_str}")
    
    if not title:
        return HttpResponse("Task title is required", status=400)
    
    try:
        task.title = title
        task.due_date = due_date
        task.save()
        logger.info(f"Task {task.id} updated successfully")
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return HttpResponse(f"Error updating task: {str(e)}", status=500)
    
    # Return the updated task HTML
    due_date_html = ''
    if task.due_date:
        due_date_html = f'''
                        <div class="text-xs text-base-content/60 mt-1 flex items-center gap-1">
                            <span class="icon-[tabler--calendar] size-3"></span>
                            {task.due_date.strftime("%b %d")}
                        </div>'''
    
    html = f'''<div class="task-item card bg-base-100 shadow-sm hover:shadow-md p-3 cursor-move" 
         draggable="true" 
         data-task-id="{task.id}"
         id="task-{task.id}">
        <div class="flex items-start justify-between gap-2">
            <div class="flex-1">
                <p class="text-sm font-medium">{task.title}</p>{due_date_html}
            </div>
            <div class="dropdown dropdown-end">
                <div tabindex="0" role="button" class="btn btn-ghost btn-xs btn-square">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                </div>
                <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-32">
                    <li><a class="edit-task-btn" data-task-id="{task.id}" data-task-title="{task.title}" data-task-due-date="{task.due_date.strftime('%Y-%m-%d') if task.due_date else ''}">Edit</a></li>
                    <li><a class="delete-task-btn" data-task-id="{task.id}">Delete</a></li>
                </ul>
            </div>
        </div>
    </div>'''
    
    return HttpResponse(html)

def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    return render(request, 'projects/partials/task_item.html', {'task': task})

@require_http_methods(["DELETE", "POST"])
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return HttpResponse("")

def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'project': project})

@require_http_methods(["DELETE", "POST"])
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    if request.htmx:
        return HttpResponse("")
    return redirect('project_list')
