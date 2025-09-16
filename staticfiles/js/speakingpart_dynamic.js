(function(){
    var $ = window.django ? window.django.jQuery : window.jQuery;
    if(!$) return setTimeout(arguments.callee, 100);

    function initSpeakingPart(inline){
        var partSelect = inline.find('select[name$="-part_type"]');
        var titleField = inline.find('.field-title');
        var subQuestionField = inline.find('.field-sub_question');
        var youShouldSayField = inline.find('.field-you_should_say');
        var subtitleField = inline.find('.field-subtitle');
        var subQuestionsField = inline.find('.field-sub_questions');

        function updateVisibility(){
            var part = partSelect.val();

            // Hide all first
            titleField.hide();
            subQuestionField.hide();
            youShouldSayField.hide();
            subtitleField.hide();
            subQuestionsField.hide();

            if(part === 'part1'){
                titleField.show();
                subQuestionsField.show(); // Part1 savollarni shu maydonga yozadi
            } else if(part === 'part2'){
                titleField.show();
                subQuestionField.show();
                youShouldSayField.show();
            } else if (part === 'part3') {
                titleField.show();
                subtitleField.show();
                subQuestionsField.show();
            }
        }

        partSelect.off('change.dynamic').on('change.dynamic', updateVisibility);
        updateVisibility();
    }

    function initAll(){
        $('.inline-related').each(function(){
            initSpeakingPart($(this));
        });

        $(document).on('formset:added', function(event, $row){
            initSpeakingPart($row);
        });

        $(document).on('djnesting:added', function(){
            $('.inline-related').each(function(){
                initSpeakingPart($(this));
            });
        });
    }

    $(document).ready(initAll);
})();
