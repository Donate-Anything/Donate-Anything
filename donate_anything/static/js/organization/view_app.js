// Code for viewing application and editing/suggesting
const ncsrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

$(document).ready(function() {
    let converter = new showdown.Converter();
    converter.setFlavor('github');
    $("#org-description").html(converter.makeHtml(document.getElementById("org-description").innerHTML));
    $("#org-instructions").html(converter.makeHtml(document.getElementById("org-instructions").innerHTML));
    let legalDoc = document.getElementById("org-legal-doc");
    if (legalDoc) {
        legalDoc.innerHTML = converter.makeHtml(legalDoc.innerHTML);
    }

    let suggestionForm = $("#add-suggestion-form");
    suggestionForm.submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: suggestionForm.attr("method"),
            url: suggestionForm.attr("action"),
            data: suggestionForm.serialize(),
            success: function (data) {
                console.log(data)
                $("#suggestEditModal").modal("hide");
                $("#responseSuccessModal").modal("show");
                // TODO Show new suggestion in sidebar
            },
            error: function (_) {
                $("#responseFailModal").modal("show");
            }
        });
    })
})

function configAddSuggestion(entity_id) {
    document.getElementById("id_id").value = entity_id;
    document.getElementById("id_create").value = "true";
}

function configEditSuggestion(edit_id) {
    // TODO Implement edit
    document.getElementById("id_id").value = edit_id;
    document.getElementById("id_create").value = "false";
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", ncsrftoken);
        }
    }
})
