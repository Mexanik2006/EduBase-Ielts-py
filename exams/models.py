from django.db import models
from django.contrib.auth.models import User
from groups.models import Group
from django.core.exceptions import ValidationError


class Exam(models.Model):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

    SECTION_TYPES = [
        (LISTENING, "Listening"),
        (READING, "Reading"),
        (WRITING, "Writing"),
        (SPEAKING, "Speaking"),
    ]

    title = models.CharField(max_length=255)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(default=60, help_text="Time in minutes")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_section_type_display()})"


class ExamAssignment(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='assignments')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    all_groups = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam', 'group']

    def __str__(self):
        if self.all_groups:
            return f"{self.exam.title} - All Groups"
        return f"{self.exam.title} - {self.group.name}"


# Reading Models
class ReadingPassage(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="reading_passages")
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    content = models.TextField()
    time = models.PositiveIntegerField(default=20, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exam.title} - Passage {self.order}: {self.title}"


class ReadingQuestion(models.Model):
    MCQ = "mcq"
    MCQ_MULTIPLE_ANSWER = "mcq_multiple_answer"
    TRUE_FALSE_NOT_GIVEN = "true_false_not_given"
    YES_NO_NOT_GIVEN = "yes_no_not_given"
    MATCHING_HEADINGS = "matching_headings"
    MATCHING_INFORMATION = "matching_information"
    ONE_WORD_AND_OR_A_NUMBER = "one_word_and_or_a_number"
    NO_WORD_AND_OR_A_NUMBER = "no_word_and_or_a_number"
    ONE_WORD_ONLY = "one_word_only"

    QUESTION_TYPES = [
        (MCQ, "Multiple Choice"),
        (MCQ_MULTIPLE_ANSWER, "Multiple Choice Multiple Answer"),
        (TRUE_FALSE_NOT_GIVEN, "True/False/Not Given"),
        (YES_NO_NOT_GIVEN, "Yes/No/Not Given"),
        (MATCHING_HEADINGS, "Matching Headings"),
        (MATCHING_INFORMATION, "Matching Information"),
        (ONE_WORD_AND_OR_A_NUMBER, "One Word and/or a Number"),
        (NO_WORD_AND_OR_A_NUMBER, "No more than a Word and/or a Number"),
        (ONE_WORD_ONLY, "One Word Only"),
    ]

    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default=MCQ)
    start_number = models.PositiveIntegerField(blank=True, null=True)
    end_number = models.PositiveIntegerField(blank=True, null=True)
    instruction = models.TextField(blank=True, help_text="Instructions for matching questions, etc.")
    
    @property
    def question_count(self):
        return (self.end_number - self.start_number + 1) if self.end_number and self.start_number else 0
    
    def __str__(self):
        return f"Q{self.start_number}-{self.end_number}: {self.get_question_type_display()}"

    def clean(self):
        super().clean()
        if self.start_number and self.end_number and self.start_number > self.end_number:
            raise ValidationError("Start number cannot be greater than end number")

    def save(self, *args, **kwargs):
        # Avval start va end raqamni to'g'rilaymiz
        if self.start_number and not self.end_number:
            self.end_number = self.start_number
        elif self.start_number and self.end_number and self.start_number > self.end_number:
            self.end_number = self.start_number

        # ✅ Avval parent obyektni saqlash
        super().save(*args, **kwargs)

        # ✅ Endi subquestions yaratamiz (faqat ID mavjud bo'lgandan keyin)
        if self.start_number and self.end_number:
            if self.question_type == self.MCQ_MULTIPLE_ANSWER:
                required_count = 1  # Har doim faqat 1ta sub-question
            else:
                required_count = self.end_number - self.start_number + 1
            
            existing_subs = list(self.subquestions.all())

            # Remove extra subquestions if count decreased
            if len(existing_subs) > required_count:
                for sub in existing_subs[required_count:]:
                    sub.delete()

            # Add missing subquestions
            for i in range(len(existing_subs), required_count):
                ReadingSubQuestion.objects.create(
                    questions=self,
                )

class ReadingSubQuestion(models.Model):
    questions = models.ForeignKey(ReadingQuestion, on_delete=models.CASCADE, related_name="subquestions")
    text = models.TextField()

    # For multiple choice
    choice_a = models.CharField(max_length=255, blank=True, null=True)
    choice_b = models.CharField(max_length=255, blank=True, null=True)
    choice_c = models.CharField(max_length=255, blank=True, null=True)
    choice_d = models.CharField(max_length=255, blank=True, null=True)
    choice_e = models.CharField(max_length=255, blank=True, null=True)

    options_list = models.TextField(blank=True, help_text="For matching questions - list of options separated by new lines")

    # For fill in the blank and one word answer questions
    title = models.CharField(max_length=255, blank=True, null=True)

    # Correct answer
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text[:50]}... (Answer: {self.correct_answer})"
    
    @property
    def section_count(self):
        if not self.options_list:
            return 0
        return len(self.options_list.split())


# Listening Models
class ListeningAudio(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="listening_audios")
    audio_file = models.FileField(upload_to="listening/")
    transcript = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exam.title} - Audio {self.order}"


class ListeningQuestion(models.Model):
    MCQ = "mcq"
    MCQ_MULTIPLE_ANSWER = "mcq_multiple_answer"
    TRUE_FALSE_NOT_GIVEN = "true_false_not_given"
    YES_NO_NOT_GIVEN = "yes_no_not_given"
    MATCHING_HEADINGS = "matching_headings"
    MATCHING_INFORMATION = "matching_information"
    ONE_WORD_AND_OR_A_NUMBER = "one_word_and_or_a_number"
    ONE_WORD_ONLY = "one_word_only"
    NO_WORD_AND_OR_A_NUMBER = "no_word_and_or_a_number"

    QUESTION_TYPES = [
        (MCQ, "Multiple Choice"),
        (MCQ_MULTIPLE_ANSWER, "Multiple Choice Multiple Answer"),
        (TRUE_FALSE_NOT_GIVEN, "True/False/Not Given"),
        (YES_NO_NOT_GIVEN, "Yes/No/Not Given"),
        (MATCHING_HEADINGS, "Matching Headings"),
        (MATCHING_INFORMATION, "Matching Information"),
        (ONE_WORD_AND_OR_A_NUMBER, "One Word and/or a Number"),
        (ONE_WORD_ONLY, "One Word Only"),
        (NO_WORD_AND_OR_A_NUMBER, "No more than a Word and/or a Number"),
    ]

    audio = models.ForeignKey(ListeningAudio, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default=MCQ)
    start_number = models.PositiveIntegerField(blank=True, null=True)
    end_number = models.PositiveIntegerField(blank=True, null=True)
    instruction = models.TextField(blank=True, help_text="Instructions for matching questions, etc.")

    def __str__(self):
        return f"Q{self.start_number}-{self.end_number}: {self.get_question_type_display()}"

    def clean(self):
        super().clean()
        if self.start_number and self.end_number and self.start_number > self.end_number:
            raise ValidationError("Start number cannot be greater than end number")

    def save(self, *args, **kwargs):
        # Ensure end_number is at least start_number
        if self.start_number and not self.end_number:
            self.end_number = self.start_number
        elif self.start_number and self.end_number and self.start_number > self.end_number:
            self.end_number = self.start_number

        super().save(*args, **kwargs)

        # Create or update subquestions based on the range
        if self.start_number and self.end_number:
            if self.question_type == self.MCQ_MULTIPLE_ANSWER:
                required_count = 1  # Har doim faqat 1ta sub-question
            else:
                required_count = self.end_number - self.start_number + 1
            
            current_subquestions = list(self.subquestions.all())

            # Remove extra subquestions
            if len(current_subquestions) > required_count:
                for subquestion in current_subquestions[required_count:]:
                    subquestion.delete()

            # Add missing subquestions
            for i in range(len(current_subquestions), required_count):
                ListeningSubQuestion.objects.create(
                    questions=self,
                    text=f"Question {self.start_number + i}"
                )


class ListeningSubQuestion(models.Model):
    questions = models.ForeignKey(ListeningQuestion, on_delete=models.CASCADE, related_name="subquestions")
    text = models.TextField()

    # For multiple choice
    choice_a = models.CharField(max_length=255, blank=True, null=True)
    choice_b = models.CharField(max_length=255, blank=True, null=True)
    choice_c = models.CharField(max_length=255, blank=True, null=True)
    choice_d = models.CharField(max_length=255, blank=True, null=True)
    choice_e = models.CharField(max_length=255, blank=True, null=True)

    options_list = models.TextField(blank=True, help_text="For matching questions - list of options separated by new lines")
    title = models.CharField(max_length=255, blank=True, null=True)

    # Correct answer
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text[:50]}... (Answer: {self.correct_answer})"


# Writing Models
class WritingTask(models.Model):
    TASK1 = "task1"
    TASK2 = "task2"

    TASK_TYPES = [
        (TASK1, "Task 1"),
        (TASK2, "Task 2"),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="writing_tasks")
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default=TASK1)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="writing_images/", blank=True, null=True)
    min_words = models.IntegerField(default=150)
    time_limit = models.PositiveIntegerField(default=20, help_text="Time in minutes")

    def __str__(self):
        return f"{self.exam.title} - {self.get_task_type_display()}: {self.title}"


# Speaking Models
class SpeakingPart(models.Model):
    PART1 = "part1"
    PART2 = "part2"
    PART3 = "part3"

    PART_TYPES = [
        (PART1, "Part 1"),
        (PART2, "Part 2"),
        (PART3, "Part 3"),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="speaking_parts")
    part_type = models.CharField(max_length=20, choices=PART_TYPES)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    questions = models.TextField(help_text="Enter questions separated by new lines")
    time_limit = models.PositiveIntegerField(default=5, help_text="Time in minutes")

    def __str__(self):
        return f"{self.exam.title} - {self.get_part_type_display()}: {self.title}"
    
    # SpeakingPart modeliga qo'shing (models.py faylida)
    def get_questions_list(self):
        """Old structure compatibility - questions from text field"""
        if self.questions:
            return [q.strip() for q in self.questions.split('\n') if q.strip()]
        return []       


class SpeakingSubQuestion(models.Model):
    part = models.ForeignKey(SpeakingPart, on_delete=models.CASCADE, related_name="sub_questions")
    text = models.TextField()
    kind = models.CharField(
        max_length=20,
        choices=[('part1', 'Part1 question'), ('part2', 'Part2 you should say'), ('part3', 'Part3 sub question')],
        default='part1'
    )

    def __str__(self):
        return f"{self.part} - {self.text[:50]}"
