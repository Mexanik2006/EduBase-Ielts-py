from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Group(models.Model):
    name = models.CharField(max_length=255)
    mentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'mentor'},
        related_name='mentor_groups'  # endi mentor.groups orqali barcha guruhlarini olish mumkin
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.mentor.get_full_name() or self.mentor.username}"

class GroupStudent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students')
    student = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'student'},
        related_name='student_group'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['group', 'student']
    
    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.group.name}"
    
    def clean(self):
        # Check if student already in another group
        if self.student and GroupStudent.objects.filter(student=self.student).exclude(pk=self.pk).exists():
            raise ValidationError("Bu talaba allaqachon boshqa guruhda.")
