; (() => {
    var $ = window.jQuery // Declare jQuery variable

    if (!$)
        return setTimeout(() => {
            updateListeningSubQuestions(updateListeningSubQuestions)
        }, 100)

    // Function to get field configuration for each question type
    function getFieldConfig(questionType) {
        const configs = {
            mcq: {
                fields: ["text", "correct_answer", "choice_a", "choice_b", "choice_c", "choice_d"],
                labels: {
                    text: "Question",
                    correct_answer: "Correct Answer (A/B/C/D)",
                },
                placeholders: {
                    correct_answer: "A/B/C/D",
                },
                selectOptions: {
                    correct_answer: ["A", "B", "C", "D"],
                },
            },
            mcq_multiple_answer: {
                fields: ["text", "options_list", "correct_answer"],
                labels: {
                    text: "Question",
                    options_list: "Answer Options (one per line)",
                    correct_answer: "Correct Answers (multiple selection allowed)",
                },
                placeholders: {
                    options_list: "Enter each option on a new line",
                    correct_answer: "Select multiple correct answers",
                },
                multiSelect: true, // Bu field multi-select ekanligini belgilaydi
            },
            true_false_not_given: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Statement",
                    correct_answer: "Answer (True/False/Not Given)",
                },
                placeholders: {
                    correct_answer: "True/False/Not Given",
                },
                selectOptions: {
                    correct_answer: ["True", "False", "Not Given"],
                },
            },
            yes_no_not_given: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Statement",
                    correct_answer: "Answer (Yes/No/Not Given)",
                },
                placeholders: {
                    correct_answer: "Yes/No/Not Given",
                },
                selectOptions: {
                    correct_answer: ["Yes", "No", "Not Given"],
                },
            },
            fill_blank: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Sentence with Blank",
                    correct_answer: "Missing Word/Phrase",
                },
                placeholders: {
                    correct_answer: "Enter missing word/phrase",
                },
            },
            matching_headings: {
                fields: ["title", "options_list", "text", "correct_answer"],
                labels: {
                    text: "Paragraph/Section",
                    correct_answer: "Heading Number/Letter",
                    options_list: "List of Headings (one per line)",
                },
                placeholders: {
                    correct_answer: "i, ii, iii or A, B, C",
                    options_list: "Enter headings separated by new lines",
                },
                selectOptions: {
                    correct_answer: [
                        "i",
                        "ii",
                        "iii",
                        "iv",
                        "v",
                        "vi",
                        "vii",
                        "viii",
                        "ix",
                        "x",
                        "A",
                        "B",
                        "C",
                        "D",
                        "E",
                        "F",
                        "G",
                        "H",
                    ],
                },
            },
            matching_information: {
                fields: ["text", "correct_answer", "options_list"],
                labels: {
                    text: "Information/Statement",
                    correct_answer: "Paragraph Letter",
                    options_list: "Paragraph Options (A, B, C, etc.)",
                },
                placeholders: {
                    correct_answer: "A/B/C/D/E/F/G",
                    options_list: "A\nB\nC\nD\nE\nF\nG",
                },
                selectOptions: {
                    correct_answer: ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
                },
            },
            matching_features: {
                fields: ["text", "correct_answer", "options_list"],
                labels: {
                    text: "Item to Match",
                    correct_answer: "Feature Letter/Number",
                    options_list: "List of Features (one per line)",
                },
                placeholders: {
                    correct_answer: "A/B/C or 1/2/3",
                    options_list: "Enter features separated by new lines",
                },
                selectOptions: {
                    correct_answer: ["A", "B", "C", "D", "E", "F", "G", "H", "1", "2", "3", "4", "5", "6", "7", "8"],
                },
            },
            sentence_completion: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Incomplete Sentence",
                    correct_answer: "Completion (max 3 words)",
                },
                placeholders: {
                    correct_answer: "Maximum 3 words from passage",
                },
            },
            summary_completion: {
                fields: ["text", "correct_answer", "options_list"],
                labels: {
                    text: "Summary with Gap",
                    correct_answer: "Missing Word/Phrase",
                    options_list: "Word Bank (if applicable)",
                },
                placeholders: {
                    correct_answer: "Word or phrase from passage",
                    options_list: "List of words (if word bank provided)",
                },
            },
            note_completion: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Note with Gap",
                    correct_answer: "Missing Information",
                },
                placeholders: {
                    correct_answer: "Word or phrase from passage",
                },
            },
            table_completion: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Table Cell Description",
                    correct_answer: "Missing Information",
                },
                placeholders: {
                    correct_answer: "Word or phrase from passage",
                },
            },
            flow_chart_completion: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Flow Chart Step",
                    correct_answer: "Missing Information",
                },
                placeholders: {
                    correct_answer: "Word or phrase from passage",
                },
            },
            diagram_labeling: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Diagram Part Description",
                    correct_answer: "Label",
                },
                placeholders: {
                    correct_answer: "Word or phrase from passage",
                },
            },
            short_answer: {
                fields: ["text", "correct_answer"],
                labels: {
                    text: "Question",
                    correct_answer: "Answer (max 3 words)",
                },
                placeholders: {
                    correct_answer: "Maximum 3 words from passage",
                },
            },
            one_word_and_or_a_number: {
                fields: ["text", "correct_answer"], // title bu yerda bo'lmaydi
                labels: {
                    text: "Question",
                    correct_answer: "Answer (max 3 words)",
                },
                placeholders: {
                    correct_answer: "Maximum 3 words from passage",
                },
            },
            one_word_only: {
                fields: ["text", "correct_answer"], // title bu yerda bo'lmaydi
                labels: {
                    text: "Question",
                    correct_answer: "Answer (max 3 words)",
                },
                placeholders: {
                    correct_answer: "Maximum 3 words from passage",
                },
            },
             no_word_and_or_a_number: {
                fields: ["text", "correct_answer"], // title bu yerda bo'lmaydi
                labels: {
                    text: "Question",
                    correct_answer: "Answer (max 3 words)",
                },
                placeholders: {
                    correct_answer: "Maximum 3 words from passage",
                },
            },
        }

        return configs[questionType] || configs["mcq"]
    }

    function convertToSelect($field, options, currentValue) {
        var $input = $field.find('input[id$="-correct_answer"]')
        if ($input.length === 0) return

        var inputId = $input.attr("id")
        var inputName = $input.attr("name")
        var inputClass = $input.attr("class") || ""

        var $select = $("<select></select>").attr("id", inputId).attr("name", inputName).addClass(inputClass)
        $select.append('<option value="">---------</option>')

        options.forEach((option) => {
            var $option = $("<option></option>").attr("value", option).text(option)
            if (currentValue === option) $option.attr("selected", "selected")
            $select.append($option)
        })

        $input.replaceWith($select)
    }

    function convertToMultiSelect($field, options, currentValues) {
        var $input = $field.find('input[id$="-correct_answer"], select[id$="-correct_answer"]')
        if ($input.length === 0) return

        var inputId = $input.attr("id")
        var inputName = $input.attr("name")
        var inputClass = $input.attr("class") || ""

        // Current values ni array qilib olish
        var selectedValues = []
        if (typeof currentValues === "string" && currentValues) {
            selectedValues = currentValues.split(",").map((v) => v.trim())
        }

        var $select = $("<select></select>")
            .attr("id", inputId)
            .attr("name", inputName)
            .addClass(inputClass)
            .attr("multiple", "multiple")
            .attr("size", Math.min(options.length, 6))

        options.forEach((option) => {
            var $option = $("<option></option>").attr("value", option).text(option)
            if (selectedValues.includes(option)) {
                $option.attr("selected", "selected")
            }
            $select.append($option)
        })

        // Multi-select o'zgarishlarini kuzatish
        $select.on("change", function () {
            var selected = $(this).val() || []
            $(this).siblings('input[type="hidden"]').remove()

            // Hidden input yaratish Django uchun
            var hiddenInput = $('<input type="hidden">').attr("name", inputName).val(selected.join(", "))

            $(this).after(hiddenInput)
        })

        $input.replaceWith($select)

        // Initial hidden input yaratish
        if (selectedValues.length > 0) {
            var hiddenInput = $('<input type="hidden">').attr("name", inputName).val(selectedValues.join(", "))
            $select.after(hiddenInput)
        }
    }

    function convertToInput($field, placeholder, currentValue) {
        var $select = $field.find('select[id$="-correct_answer"]')
        if ($select.length === 0) return

        var selectId = $select.attr("id")
        var selectName = $select.attr("name")
        var selectClass = $select.attr("class") || ""

        var $input = $('<input type="text">')
            .attr("id", selectId)
            .attr("name", selectName)
            .addClass(selectClass)
            .attr("placeholder", placeholder)
            .val(currentValue)

        $select.replaceWith($input)
    }

    function updateListeningSubQuestions($questionForm) {
        var questionType = $questionForm.find('select[id$="-question_type"]').val()
        var startNumber = Number.parseInt($questionForm.find('input[id$="-start_number"]').val()) || 0
        var endNumber = Number.parseInt($questionForm.find('input[id$="-end_number"]').val()) || 0

        var subquestionCount
        if (questionType === "mcq_multiple_answer") {
            subquestionCount = 1
        } else {
            subquestionCount = Math.max(0, endNumber - startNumber + 1)
        }

        if (isNaN(subquestionCount) || subquestionCount <= 0) return

        var fieldConfig = getFieldConfig(questionType)

        $questionForm
            .find('.djn-group[data-inline-model="exams-listeningsubquestion"] .djn-inline-form:not(.djn-empty-form)')
            .each(function (index) {
                var $form = $(this)
                var questionNumber = startNumber + index

                $form
                    .find(
                        ".field-choice_a, .field-choice_b, .field-choice_c, .field-choice_d, .field-choice_e, .field-choice_f, .field-choice_g, .field-choice_h, .field-options_list",
                    )
                    .hide()

                // 🔑 Title boshqaruvi
                var $titleField = $form.find(".field-title")
                if ((questionType === "one_word_and_or_a_number" || questionType === "one_word_only" || questionType === "no_word_and_or_a_number") && index === 0) {
                    $titleField.show()
                    $titleField.find("label").text("Title")
                } else {
                    $titleField.hide()
                }

                // Show required fields and update labels
                fieldConfig.fields.forEach((fieldName) => {
                    var $field = $form.find(".field-" + fieldName)

                    if (
                        fieldName === "title" &&
                        (questionType === "one_word_and_or_a_number" || questionType === "one_word_only" || questionType === "no_word_and_or_a_number")
                    ) {
                        if (index === 0) {
                            $field.show()
                            $field.find("label").text("Title")
                        } else {
                            $field.hide()
                        }
                        return
                    }

                    // 🔑 matching_headings uchun title va options_list boshqaruvi
                    if (questionType === "matching_headings") {
                        if (index === 0) {
                            // Title field
                            var $titleField = $form.find(".field-title")
                            $titleField.show()
                            $titleField.find("label").text("Title")

                            // Options_list field
                            var $optionsField = $form.find(".field-options_list")
                            $optionsField.show()
                            $optionsField.find("label").text("List of Headings (one per line)")

                            // 🔥 options_list ni title'dan keyin chiqaramiz
                            var $titleRow = $titleField.closest(".form-row")
                            var $optionsRow = $optionsField.closest(".form-row")

                            if ($optionsRow.length && $titleRow.length) {
                                $optionsRow.detach().insertAfter($titleRow)
                            }
                        } else {
                            // boshqa subquestionlarda yashirish
                            $form.find(".field-title").hide()
                            $form.find(".field-options_list").hide()
                        }
                    }

                    if (questionType === "mcq_multiple_answer" && fieldName === "options_list") {
                        $field.show()
                        $field.find("label").text("Answer Options (one per line)")

                        // options_list o'zgarishini kuzatish
                        $field.find("textarea").on("input", () => {
                            updateMultiSelectFromOptions($form, questionType)
                        })
                    }

                    // boshqa fieldlarni default ko'rsatish
                    $field.show()

                    if (fieldConfig.labels[fieldName]) {
                        var label = fieldConfig.labels[fieldName]
                        if (fieldName === "text" || fieldName === "correct_answer") {
                            if (questionType !== "mcq_multiple_answer") {
                                label = label + " " + questionNumber
                            }
                        }
                        $field.find("label").text(label)
                    }

                    if (fieldName === "correct_answer") {
                        var currentValue = $field.find("input, select").val() || ""

                        if (questionType === "mcq_multiple_answer") {
                            updateMultiSelectFromOptions($form, questionType)
                        } else if (questionType === "matching_headings") {
                            // options_list qiymatlarini select qilib ko'rsatish
                            var optionsText = $questionForm.find(".field-options_list textarea").val() || ""
                            var options = optionsText
                                .split("\n")
                                .map((s) => s.trim())
                                .filter((s) => s.length > 0)

                            if (options.length > 0) {
                                convertToSelect($field, options, currentValue)
                            } else {
                                convertToInput($field, "Enter heading number/letter", currentValue)
                            }
                        } else if (fieldConfig.selectOptions && fieldConfig.selectOptions[fieldName]) {
                            convertToSelect($field, fieldConfig.selectOptions[fieldName], currentValue)
                        } else {
                            var placeholder = fieldConfig.placeholders[fieldName] || ""
                            convertToInput($field, placeholder, currentValue)
                        }
                    } else {
                        if (fieldConfig.placeholders[fieldName]) {
                            $field.find("input, textarea").attr("placeholder", fieldConfig.placeholders[fieldName])
                        }
                    }
                })

                var $title = $form.find("h3.djn-drag-handler")
                if ($title.length === 0) {
                    var titleText =
                        questionType === "mcq_multiple_answer"
                            ? '<b>Multiple Choice Multiple Answer:</b>&nbsp;<span class="inline_label">#' + startNumber + "</span>"
                            : '<b>Listening sub question:</b>&nbsp;<span class="inline_label">#' + questionNumber + "</span>"

                    $form.prepend(
                        '<h3 class="djn-drag-handler">' +
                        titleText +
                        '<span><a class="inline-deletelink djn-remove-handler djn-level-3 djn-model-exams-listeningsubquestion" href="javascript:void(0)">Remove</a></span></h3>',
                    )
                } else {
                    var labelText = questionType === "mcq_multiple_answer" ? "#" + startNumber : "#" + questionNumber
                    $title.find(".inline_label").text(labelText)
                }
            })
    }

    function updateMultiSelectFromOptions($form, questionType) {
        if (questionType !== "mcq_multiple_answer") return

        var $optionsField = $form.find(".field-options_list")
        var $correctAnswerField = $form.find(".field-correct_answer")

        var optionsText = $optionsField.find("textarea").val() || ""
        var options = optionsText
            .split("\n")
            .map((s) => s.trim())
            .filter((s) => s.length > 0)

        if (options.length > 0) {
            var currentValue = $correctAnswerField.find("input, select").val() || ""
            convertToMultiSelect($correctAnswerField, options, currentValue)
        }
    }

    $(document).ready(() => {
        $(document).on(
            "change",
            'select[id$="-question_type"], input[id$="-start_number"], input[id$="-end_number"]',
            function () {
                var $questionForm = $(this).closest(".djn-inline-form")
                if (
                    $questionForm.find(
                        '.djn-group[data-inline-model="exams-listeningsubquestion"] .djn-inline-form:not(.djn-empty-form)',
                    ).length > 0
                ) {
                    updateListeningSubQuestions($questionForm)
                }
            },
        )

        $('.djn-group[data-inline-model="exams-listeningquestion"] .djn-inline-form:not(.djn-empty-form)').each(
            function () {
                updateListeningSubQuestions($(this))
            },
        )
    })

    $(document).on("formset:added", (event, $row, formsetName) => {
        if (formsetName && formsetName.indexOf("questions") > -1) {
            $row.find('select[id$="-question_type"]').val("mcq")
            $row.find('input[id$="-start_number"]').val("1")
            $row.find('input[id$="-end_number"]').val("1")

            $row
                .find('select[id$="-question_type"], input[id$="-start_number"], input[id$="-end_number"]')
                .on("change", function () {
                    var $questionForm = $(this).closest(".djn-inline-form")
                    if (
                        $questionForm.find(
                            '.djn-group[data-inline-model="exams-listeningsubquestion"] .djn-inline-form:not(.djn-empty-form)',
                        ).length > 0
                    ) {
                        updateListeningSubQuestions($questionForm)
                    }
                })
        }
    })
})(window.django ? window.django.jQuery : window.jQuery)
