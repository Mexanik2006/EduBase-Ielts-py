(function(){
    var $ = window.django ? window.django.jQuery : window.jQuery;
    if(!$) return setTimeout(arguments.callee, 100);

    function toggleFields(inline){
        var sectionSelect = inline.find('select[name$="-task_type"]');
        var imgField = inline.find('.field-image');

        function updateVisibility(){
            var value = sectionSelect.val();
            if(value === 'task1'){
                imgField.show();
            } else {
                imgField.hide();
            }
        }

        sectionSelect.off('change.toggle').on('change.toggle', updateVisibility);
        updateVisibility();
    }

    function initAll(){
        $('.inline-related').each(function(){
            toggleFields($(this));
        });

        $(document).on('formset:added', function(event, $row){
            toggleFields($row);
        });

        $(document).on('djnesting:added', function(){
            $('.inline-related').each(function(){
                toggleFields($(this));
            });
        });
    }

    $(document).ready(initAll);
})();
