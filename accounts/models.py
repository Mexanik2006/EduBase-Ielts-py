from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ADMIN = 'admin'
    MENTOR = 'mentor'
    STUDENT = 'student'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MENTOR, 'Mentor'),
        (STUDENT, 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Har safar yangi User yaratilganda avtomatik Profile ham yaratiladi.
    Shu bilan birga first_name va last_name bo'sh bo'lsa, ularni default qiymat bilan to'ldiramiz.
    """
    if created:
        # Profile yaratish
        Profile.objects.get_or_create(user=instance)

        # Agar ism va familiya berilmagan bo‘lsa, default qilib username asosida to‘ldiramiz
        if not instance.first_name:
            instance.first_name = ""
        if not instance.last_name:
            instance.last_name = ""
        instance.save()
