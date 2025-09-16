from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Attempt, Review, AttemptAudio
from exams.models import Exam
from groups.models import Group, GroupStudent

@login_required
def submit_attempt(request, exam_id):
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST method required'}, status=405)

        exam = get_object_or_404(Exam, id=exam_id)

        if request.user.profile.role != 'student':
            return JsonResponse({'error': 'Only students can submit attempts'}, status=403)

        # Talabaning guruhi
        try:
            student_group = GroupStudent.objects.get(student=request.user).group
        except GroupStudent.DoesNotExist:
            student_group = None

        # Attempt yaratish yoki olish
        attempt, created = Attempt.objects.get_or_create(
            exam=exam,
            student=request.user,
            defaults={
                'group': student_group,
                'status': 'submitted',
                'submitted_at': timezone.now(),
            }
        )

        if not created and attempt.status != 'in_progress':
            return JsonResponse({'error': 'Attempt already submitted'}, status=400)

        # Text javoblar
        answers = {}
        for key in request.POST.keys():
            norm_key = key[:-2] if key.endswith('[]') else key

            # q_... (reading/listening), part_... (speaking), task_... (writing)
            if norm_key.startswith(('q_', 'part_', 'task_')):
                values = request.POST.getlist(key)
                answers[norm_key] = values if len(values) > 1 else values[0]

        attempt.answers = json.dumps(answers)

        for key, file in request.FILES.items():
            if key.endswith('_audio'):
                # Extract part ID from key like 'speaking_part_1_audio'
                try:
                    part_id = int(key.split('_')[-2])  # Get the number before '_audio'
                    
                    # Create or update audio file for this part
                    audio_obj, created = AttemptAudio.objects.get_or_create(
                        attempt=attempt,
                        part_id=part_id,
                        defaults={'audio_file': file}
                    )
                    
                    if not created:
                        # Update existing audio file
                        audio_obj.audio_file = file
                        audio_obj.save()
                        
                except (ValueError, IndexError):
                    # If we can't extract part_id, skip this file
                    continue

        # Status va vaqt
        attempt.status = 'submitted'
        attempt.submitted_at = timezone.now()

        # Agar Reading/Listening bo'lsa, avtomatik baholash
        if exam.section_type in ['reading', 'listening']:
            score = calculate_auto_score(exam, answers)
            if exam.section_type == 'reading':
                attempt.reading_score = score
            else:
                attempt.listening_score = score
            attempt.total_score = score
            attempt.status = 'completed'
            attempt.completed_at = timezone.now()

        attempt.save()

        return JsonResponse({
            'success': True,
            'message': 'Javoblar muvaffaqiyatli yuborildi!',
            'redirect_url': f'/exams/{exam_id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)
    
def normalize_answer(ans):
    """Faqat variant harfini qaytaradi (A, B, C ...)"""
    if not ans:
        return ""
    if isinstance(ans, list):  # agar list bo‘lsa
        ans = ans[0]           # faqat birinchi elementni olamiz
    ans = str(ans).strip()
    return ans[0].lower() if ans else ""


def calculate_auto_score(exam, answers):
    """Calculate automatic score for reading/listening exams"""
    correct_count = 0
    total_questions = 0

    if exam.section_type == 'reading':
        for passage in exam.reading_passages.all():
            for question in passage.questions.all():
                for subq in question.subquestions.all():
                    total_questions += 1
                    question_key = f"q_{subq.id}"
                    if question_key in answers:
                        student_answer = normalize_answer(answers[question_key])
                        correct_answer = normalize_answer(subq.correct_answer)

                        if student_answer == correct_answer:
                            correct_count += 1

    elif exam.section_type == 'listening':
        for audio in exam.listening_audios.all():
            for question in audio.questions.all():
                for subq in question.subquestions.all():
                    total_questions += 1
                    question_key = f"q_{subq.id}"
                    if question_key in answers:
                        student_answer = normalize_answer(answers[question_key])
                        correct_answer = normalize_answer(subq.correct_answer)

                        if student_answer == correct_answer:
                            correct_count += 1

    if total_questions == 0:
        return 0.0

    # Convert to IELTS band score (0-9 with .5 steps)
    percentage = (correct_count / total_questions) * 100

    # Har 10% = 1 ball, keyin .5 ni ham hisoblash uchun round qilyapmiz
    raw_band = percentage / 10  
    band = round(raw_band * 2) / 2  

    # Maksimal qiymat 9.0 dan oshmasligi uchun
    return min(band, 9.0)


@login_required
def review_attempt(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)

    if request.user.profile.role != 'mentor':
        messages.error(request, 'Faqat mentorlar baholash qila oladi.')
        return redirect('exams:exam_list')

    # Parse answers
    answers = {}
    if attempt.answers:
        try:
            answers = json.loads(attempt.answers)
        except json.JSONDecodeError:
            answers = {}

    # Audio files
    audio_files = {}
    if attempt.exam.section_type == 'speaking':
        for audio in attempt.audio_files.all():
            audio_files[audio.part_id] = audio.audio_file

    # Writing tasks + student answers
    writing_tasks = []
    if attempt.exam.section_type == "writing":
        for task in attempt.exam.writing_tasks.all():
            # JSONdagi keylar "task_3" ko‘rinishda
            answer = answers.get(f"task_{task.id}", None)
            writing_tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "image": task.image,
                "task_type": task.get_task_type_display(),
                "student_answer": answer,
            })

    # Band scores
    band_scores = [i * 0.5 for i in range(19)]

    # POST da baholash
    if request.method == 'POST':
        task_achievement = float(request.POST.get('task_achievement', 0))
        coherence_cohesion = float(request.POST.get('coherence_cohesion', 0))
        lexical_resource = float(request.POST.get('lexical_resource', 0))
        grammatical_range = float(request.POST.get('grammatical_range', 0))

        overall_score = (task_achievement + coherence_cohesion +
                         lexical_resource + grammatical_range) / 4

        review, created = Review.objects.get_or_create(
            attempt=attempt,
            mentor=request.user,
            defaults={
                'task_achievement': task_achievement,
                'coherence_cohesion': coherence_cohesion,
                'lexical_resource': lexical_resource,
                'grammatical_range': grammatical_range,
                'overall_score': overall_score,
                'feedback': request.POST.get('feedback', ''),
                'reviewed_at': timezone.now(),
            }
        )

        if not created:
            review.task_achievement = task_achievement
            review.coherence_cohesion = coherence_cohesion
            review.lexical_resource = lexical_resource
            review.grammatical_range = grammatical_range
            review.overall_score = overall_score
            review.feedback = request.POST.get('feedback', '')
            review.reviewed_at = timezone.now()
            review.save()

        attempt.total_score = overall_score
        attempt.status = 'completed'
        attempt.completed_at = timezone.now()
        attempt.save()

        messages.success(request, 'Baholash muvaffaqiyatli saqlandi!')
        return redirect('pending_reviews')

    context = {
        "attempt": attempt,
        "answers": answers,
        "audio_files": audio_files,
        "band_scores": band_scores,
        "writing_tasks": writing_tasks,  # ✅ endi dict list
    }

    return render(request, "attempts/review_attempt.html", context)


@login_required
def my_attempts(request):
    """View for students to see their own attempts"""
    if request.user.profile.role != 'student':
        messages.error(request, 'Faqat talabalar o\'z urinishlarini ko\'ra oladi.')
        return redirect('exams:exam_list')
    
    attempts = Attempt.objects.filter(student=request.user).order_by('-created_at')
    
    context = {
        'attempts': attempts,
    }
    
    return render(request, 'attempts/my_attempts.html', context)

@login_required
def pending_reviews(request):
    """View for mentors to see attempts pending review"""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Faqat mentorlar baholash qila oladi.')
        return redirect('exams:exam_list')
    
    # Get attempts that need review (writing and speaking only)
    pending_attempts = Attempt.objects.filter(
        status='submitted',
        exam__section_type__in=['writing', 'speaking']
    ).select_related('student', 'exam', 'group').order_by('-submitted_at')
    
    context = {
        'pending_attempts': pending_attempts,
    }
    
    return render(request, 'attempts/pending_reviews.html', context)
