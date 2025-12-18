from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from src.models.productivity import Note, TimeEntry
from src.models.projects import Project, Task


def productivity_dashboard(request):
    recent_notes = Note.objects.all()[:5]
    recent_time_entries = TimeEntry.objects.select_related("project", "task").all()[:5]
    total_tracked_hours = (
        sum(
            (
                entry.duration.total_seconds()
                for entry in recent_time_entries
                if entry.duration
            ),
            0,
        )
        / 3600
        if recent_time_entries
        else 0
    )
    return render(
        request,
        "productivity/dashboard.html",
        {
            "recent_notes": recent_notes,
            "recent_time_entries": recent_time_entries,
            "total_tracked_hours": total_tracked_hours,
        },
    )


def note_list(request):
    notes = Note.objects.all()
    return render(request, "productivity/note_list.html", {"notes": notes})


def note_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if title and content:
            Note.objects.create(title=title, content=content)
            return redirect("note_list")

    return render(request, "productivity/note_form.html")


def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if title and content:
            note.title = title
            note.content = content
            note.save()
            return redirect("note_list")

    return render(request, "productivity/note_form.html", {"note": note})


@require_http_methods(["DELETE", "POST"])
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return redirect("note_list")


def _parse_datetime(value: str):
    if not value:
        return None
    # Expect HTML datetime-local format: "YYYY-MM-DDTHH:MM"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def timeentry_list(request):
    time_entries = TimeEntry.objects.select_related("project", "task").all()
    return render(
        request,
        "productivity/timeentry_list.html",
        {"time_entries": time_entries},
    )


def timeentry_create(request):
    projects = Project.objects.all()
    tasks = Task.objects.all()

    if request.method == "POST":
        project_id = request.POST.get("project")
        task_id = request.POST.get("task")
        description = request.POST.get("description", "").strip()
        start_time_raw = request.POST.get("start_time", "").strip()
        end_time_raw = request.POST.get("end_time", "").strip()

        start_time = _parse_datetime(start_time_raw)
        end_time = _parse_datetime(end_time_raw)

        if description and start_time:
            project = (
                Project.objects.filter(id=project_id).first() if project_id else None
            )
            task = Task.objects.filter(id=task_id).first() if task_id else None

            TimeEntry.objects.create(
                project=project,
                task=task,
                description=description,
                start_time=start_time,
                end_time=end_time,
            )
            return redirect("timeentry_list")

    return render(
        request,
        "productivity/timeentry_form.html",
        {"projects": projects, "tasks": tasks},
    )


def timeentry_edit(request, pk):
    time_entry = get_object_or_404(TimeEntry, pk=pk)
    projects = Project.objects.all()
    tasks = Task.objects.all()

    if request.method == "POST":
        project_id = request.POST.get("project")
        task_id = request.POST.get("task")
        description = request.POST.get("description", "").strip()
        start_time_raw = request.POST.get("start_time", "").strip()
        end_time_raw = request.POST.get("end_time", "").strip()

        start_time = _parse_datetime(start_time_raw)
        end_time = _parse_datetime(end_time_raw)

        if description and start_time:
            time_entry.project = (
                Project.objects.filter(id=project_id).first() if project_id else None
            )
            time_entry.task = (
                Task.objects.filter(id=task_id).first() if task_id else None
            )
            time_entry.description = description
            time_entry.start_time = start_time
            time_entry.end_time = end_time
            time_entry.save()
            return redirect("timeentry_list")

    context = {
        "time_entry": time_entry,
        "projects": projects,
        "tasks": tasks,
    }
    return render(request, "productivity/timeentry_form.html", context)


@require_http_methods(["DELETE", "POST"])
def timeentry_delete(request, pk):
    time_entry = get_object_or_404(TimeEntry, pk=pk)
    time_entry.delete()
    return redirect("timeentry_list")
