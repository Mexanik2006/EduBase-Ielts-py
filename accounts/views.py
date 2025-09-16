from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from groups.models import Group, GroupStudent
from attempts.models import Attempt
from exams.models import ExamAssignment

@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Username va parol kiritish majburiy!")
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            role = getattr(user.profile, 'role', 'student')
            redirect_urls = {
                'admin': '/admin/',
                'mentor': '/mentor/',
                'student': '/student/'
            }
            return redirect(redirect_urls.get(role, '/student/'))
        else:
            messages.error(request, "Username yoki parol noto'g'ri!")
    
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    role = getattr(request.user.profile, 'role', 'student')
    
    redirect_map = {
        'admin': '/admin/',
        'mentor': 'mentor_dashboard',
        'student': 'student_dashboard'
    }
    
    return redirect(redirect_map.get(role, 'student_dashboard'))

@login_required
def mentor_dashboard(request):
    if request.user.profile.role != 'mentor':
        return redirect('dashboard')
    
    mentor_groups = Group.objects.filter(mentor=request.user).select_related('mentor')
    total_students = GroupStudent.objects.filter(group__in=mentor_groups).count()
    
    pending_reviews = Attempt.objects.filter(
        group__in=mentor_groups,
        status='submitted',
        exam__section_type__in=['writing', 'speaking']
    ).count()
    
    recent_attempts = Attempt.objects.filter(
        group__in=mentor_groups
    ).select_related('student', 'exam', 'group').order_by('-created_at')[:5]
    
    context = {
        'mentor_groups': mentor_groups,
        'total_students': total_students,
        'pending_reviews': pending_reviews,
        'recent_attempts': recent_attempts,
    }
    
    return render(request, 'accounts/mentor_dashboard.html', context)

@login_required
def student_dashboard(request):
    if request.user.profile.role != 'student':
        return redirect('dashboard')
    
    try:
        student_group = GroupStudent.objects.select_related('group').get(student=request.user).group
    except GroupStudent.DoesNotExist:
        student_group = None
    
    # Umumiy testlar sonini olib kelamiz
    if student_group:
        all_available_exams_qs = ExamAssignment.objects.filter(
            Q(group=student_group) | Q(all_groups=True)
        )
    else:
        all_available_exams_qs = ExamAssignment.objects.filter(all_groups=True)
    
    available_exams_count = all_available_exams_qs.count()
    available_exams = all_available_exams_qs.select_related('exam').order_by('-exam__created_at')[:3]
    
    # Umumiy urinishlar sonini olib kelamiz
    all_student_attempts_qs = Attempt.objects.filter(student=request.user).select_related('exam')
    student_attempts_count = all_student_attempts_qs.count()
    
    recent_attempts = all_student_attempts_qs.order_by('-created_at')[:3]
    total_attempts = student_attempts_count
    completed_attempts = all_student_attempts_qs.filter(status='completed').count()
    
    avg_score_result = all_student_attempts_qs.filter(
        status='completed', 
        total_score__isnull=False
    ).aggregate(avg_score=Avg('total_score'))
    avg_score = round(avg_score_result['avg_score'] or 0, 1)
    
    context = {
        'student_group': student_group,
        'available_exams': available_exams,
        'student_attempts': recent_attempts,
        'total_attempts': total_attempts,
        'completed_attempts': completed_attempts,
        'avg_score': avg_score,
        'available_exams_count': available_exams_count,
        'student_attempts_count': student_attempts_count,
    }
    
    return render(request, 'accounts/student_dashboard.html', context)