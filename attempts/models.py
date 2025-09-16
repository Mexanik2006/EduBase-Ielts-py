from django.db import models
from django.contrib.auth.models import User
from exams.models import Exam
from groups.models import Group

class Attempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Scores
    reading_score = models.FloatField(null=True, blank=True)
    listening_score = models.FloatField(null=True, blank=True)
    writing_score = models.FloatField(null=True, blank=True)
    speaking_score = models.FloatField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)
    
    # Answers (JSON field would be better, but using TextField for simplicity)
    answers = models.TextField(blank=True, help_text="JSON format answers")
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['exam', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title} ({self.status})"

class AttemptAudio(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='audio_files')
    part_id = models.IntegerField(help_text="Speaking part ID")
    audio_file = models.FileField(upload_to='speaking_audios/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['attempt', 'part_id']
    
    def __str__(self):
        return f"{self.attempt.student.username} - Part {self.part_id}"

class Review(models.Model):
    attempt = models.OneToOneField(Attempt, on_delete=models.CASCADE, related_name='review')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Writing/Speaking specific scores
    task_achievement = models.FloatField(null=True, blank=True)
    coherence_cohesion = models.FloatField(null=True, blank=True)
    lexical_resource = models.FloatField(null=True, blank=True)
    grammatical_range = models.FloatField(null=True, blank=True)
    
    # Overall score
    overall_score = models.FloatField()
    
    # Feedback
    feedback = models.TextField()
    
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.attempt.student.username} - {self.attempt.exam.title}"
