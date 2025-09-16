import nested_admin
from django.contrib import admin
from .models import (
    Exam, ExamAssignment, ReadingPassage, ReadingQuestion,
    ListeningAudio, ListeningQuestion, WritingTask, SpeakingPart, SpeakingSubQuestion, ReadingSubQuestion, ListeningSubQuestion
)

class ReadingSubQuestionInline(nested_admin.NestedStackedInline):
    model = ReadingSubQuestion
    extra = 0
    fields = (
        "title",
        "text",
        "correct_answer",
        "choice_a", "choice_b", "choice_c", "choice_d", "choice_e",
        "options_list", 
    )

    classes = ['reading-subquestion-inline']

class ReadingQuestionInline(nested_admin.NestedStackedInline):
    model = ReadingQuestion
    extra = 0
    fields = (
        "passage",
        "question_type",
        "instruction",
        "start_number",
        "end_number",
    )
    list_display = ['passage', 'question_type']
    inlines = [ReadingSubQuestionInline]

    class Media:
        js = ("js/readingquestion_dynamic.js",)
        css = {
            'all': ("css/readingquestion.css",)
        }

class ReadingPassageInline(nested_admin.NestedStackedInline):
    model = ReadingPassage
    extra = 0
    inlines = [ReadingQuestionInline]


class ListeningSubQuestionInline(nested_admin.NestedStackedInline):
    model = ListeningSubQuestion
    extra = 0
    fields = (
        "title",
        "text",
        "correct_answer",
        "choice_a", "choice_b", "choice_c", "choice_d", "choice_e",
        "options_list", 
    )

    classes = ['listening-subquestion-inline']

    def get_fields(self, request, obj=None):
        # Initially hide choice fields - they will be shown by JS based on question type
        return super().get_fields(request, obj)

class ListeningQuestionInline(nested_admin.NestedStackedInline):
    model = ListeningQuestion
    extra = 0
    fields = (
        "audio",
        "question_type",
        "instruction",
        "start_number",
        "end_number",
    )
    inlines = [ListeningSubQuestionInline]
    list_display = ['audio', 'question_type']

    class Media:
        js = ("js/listeningquestion_dynamic.js",)
        css = {
            'all': ("css/readingquestion.css",)
        }

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.__init__ = self.wrap_formset_init(formset.__init__)
        return formset

    def wrap_formset_init(self, old_init):
        def new_init(self, *args, **kwargs):
            result = old_init(self, *args, **kwargs)
            if self.initial_extra:
                for form in self.forms:
                    if form.initial.get('question_type') is None:
                        form.initial['question_type'] = ListeningQuestion.MCQ
                    if form.initial.get('start_number') is None:
                        form.initial['start_number'] = 1
                    if form.initial.get('end_number') is None:
                        form.initial['end_number'] = 1
            return result

        return new_init

class ListeningAudioInline(nested_admin.NestedStackedInline):
    model = ListeningAudio
    extra = 0
    inlines = [ListeningQuestionInline]
class WritingTaskInline(nested_admin.NestedStackedInline):
    model = WritingTask
    extra = 0
    fields = ('task_type', 'title', 'description', 'image', 'min_words', 'time_limit')

    class Media:
        js = ('js/writingtask_dynamic.js',)  # JS faylni ulaymiz
class SpeakingSubQuestionInline(nested_admin.NestedStackedInline):
    model = SpeakingSubQuestion
    extra = 1
    fields = ['kind', 'text']
    verbose_name = "Question"
    verbose_name_plural = "Questions"
class SpeakingPartInline(nested_admin.NestedStackedInline):
    model = SpeakingPart
    inlines = [SpeakingSubQuestionInline]
    extra = 0
    fields = ['part_type', 'title', 'subtitle']

    class Media:
        js = ('js/speakingpart_dynamic.js',)

@admin.register(Exam)
class ExamAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title', 'section_type', 'time_limit', 'is_published', 'created_at']
    list_filter = ['section_type', 'is_published', 'created_at']
    search_fields = ['title', 'description']

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if obj.section_type == Exam.READING:
            return [ReadingPassageInline(self.model, self.admin_site)]
        elif obj.section_type == Exam.LISTENING:
            return [ListeningAudioInline(self.model, self.admin_site)]
        elif obj.section_type == Exam.WRITING:
            return [WritingTaskInline(self.model, self.admin_site)]
        elif obj.section_type == Exam.SPEAKING:
            return [SpeakingPartInline(self.model, self.admin_site)]
        return []

@admin.register(ExamAssignment)
class ExamAssignmentAdmin(admin.ModelAdmin):
    list_display = ['exam', 'group', 'all_groups', 'assigned_at']
    list_filter = ['all_groups', 'assigned_at', 'exam__section_type']
    search_fields = ['exam__title', 'group__name']
