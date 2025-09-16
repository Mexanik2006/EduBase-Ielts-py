from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Group, GroupStudent


@login_required
def mentor_groups(request):
    if request.user.profile.role != 'mentor':
        return redirect('dashboard')

    # Bir mentorning barcha guruhlarini olish
    mentor_groups = Group.objects.filter(mentor=request.user)

    groups_with_students = []
    for group in mentor_groups:
        students = GroupStudent.objects.filter(group=group).select_related('student')
        groups_with_students.append({
            'group': group,
            'students': students
        })

    context = {
        'groups_with_students': groups_with_students,
    }

    return render(request, 'groups/mentor_groups.html', context)

@login_required
def student_group(request):
    if request.user.profile.role != 'student':
        return redirect('dashboard')
    
    try:
        student_group = GroupStudent.objects.get(student=request.user)
        group_students = GroupStudent.objects.filter(group=student_group.group).select_related('student')
    except GroupStudent.DoesNotExist:
        student_group = None
        group_students = []
    
    context = {
        'student_group': student_group,
        'group_students': group_students,
    }
    
    return render(request, 'groups/student_group.html', context)
