from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Exam, ExamAssignment
from groups.models import GroupStudent
from attempts.models import Attempt

@login_required
def exam_list(request):
    if request.user.profile.role == 'student':
        # Get student's group
        try:
            student_group = GroupStudent.objects.get(student=request.user).group
            # Get exams assigned to student's group or all groups
            exam_assignments = ExamAssignment.objects.filter(
                Q(group=student_group) | Q(all_groups=True)
            ).select_related('exam').prefetch_related('exam__attempts')
        except GroupStudent.DoesNotExist:
            # Student not in any group, show only all_groups exams
            exam_assignments = ExamAssignment.objects.filter(all_groups=True).select_related('exam').prefetch_related('exam__attempts')
        
        exam_data = []
        for assignment in exam_assignments:
            # Check if student has attempted this exam
            attempt = Attempt.objects.filter(
                exam=assignment.exam, 
                student=request.user
            ).first()
            
            exam_info = {
                'assignment': assignment,
                'attempt': attempt,
                'status': 'completed' if attempt else 'new'
            }
            exam_data.append(exam_info)
    else:
        # For mentors and admins, show all published exams
        exam_assignments = ExamAssignment.objects.all().select_related('exam')
        exam_data = [{'assignment': assignment, 'attempt': None, 'status': 'new'} for assignment in exam_assignments]
    
    context = {
        'exam_data': exam_data,
    }
    
    return render(request, 'exams/exam_list.html', context)

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Check if student can access this exam
    if request.user.profile.role == 'student':
        try:
            student_group = GroupStudent.objects.get(student=request.user).group
            exam_assignment = ExamAssignment.objects.filter(
                exam=exam
            ).filter(
                Q(group=student_group) | Q(all_groups=True)
            ).first()
            
            if not exam_assignment:
                messages.error(request, "Bu testga ruxsatingiz yo'q.")
                return redirect('exam_list')
        except GroupStudent.DoesNotExist:
            exam_assignment = ExamAssignment.objects.filter(exam=exam, all_groups=True).first()
            if not exam_assignment:
                messages.error(request, "Bu testga ruxsatingiz yo'q.")
                return redirect('exam_list')
    
    # Check if student already attempted this exam
    existing_attempt = None
    if request.user.profile.role == 'student':
        existing_attempt = Attempt.objects.filter(exam=exam, student=request.user).first()
    
    context = {
        'exam': exam,
        'existing_attempt': existing_attempt,
    }
    
    return render(request, 'exams/exam_detail.html', context)

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Only students can take exams
    if request.user.profile.role != 'student':
        messages.error(request, "Faqat talabalar test topshira oladi.")
        return redirect('exam_detail', exam_id=exam_id)
    
    # Check if student already attempted this exam
    existing_attempt = Attempt.objects.filter(exam=exam, student=request.user).first()
    if existing_attempt:
        messages.error(request, "Siz bu testni allaqachon topshirgansiz.")
        return redirect('exam_detail', exam_id=exam_id)
    
    # Get student's group
    try:
        student_group = GroupStudent.objects.get(student=request.user).group
    except GroupStudent.DoesNotExist:
        student_group = None
    
    # Check access
    exam_assignment = ExamAssignment.objects.filter(
        exam=exam
    ).filter(
        Q(group=student_group) | Q(all_groups=True)
    ).first()
    
    if not exam_assignment:
        messages.error(request, "Bu testga ruxsatingiz yo'q.")
        return redirect('exam_list')
    
    context = {
        'exam': exam,
        'student_group': student_group,
    }
    
    # Render different templates based on exam type
    if exam.section_type == 'reading':
        return render(request, 'exams/take_reading.html', context)
    elif exam.section_type == 'listening':
        return render(request, 'exams/take_listening.html', context)
    elif exam.section_type == 'writing':
        return render(request, 'exams/take_writing.html', context)
    elif exam.section_type == 'speaking':
        return render(request, 'exams/take_speaking.html', context)
    
    return redirect('exam_detail', exam_id=exam_id)
