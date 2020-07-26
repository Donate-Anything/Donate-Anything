// Code for viewing application and editing/suggesting
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

function handleFormSuccess(data, textStatus, jqXHR) {
    console.log(data) // nothing
    console.log(textStatus) // "success"
    console.log(jqXHR) // huge dict
    setTimeout(function() {
        $("#responseSuccessModal").modal()
    }, 3)
}

function handleFormError(jqXHR, textStatus, errorThrown){
    console.log(jqXHR)  // huge dict
    console.log(textStatus) // "error"
    console.log(errorThrown) // "Internal server error", usually
    setTimeout(function() {
        $("#responseFailModal").modal()
    }, 3)
}

$("#update-app-form").submit(function(event) {
    event.preventDefault();
    let formData = $(this).serialize()
    let thisURL = $(this).attr('data-url') || window.location.href // or set your own url
    $.ajax({
        method: "POST",
        url: thisURL,
        data: formData,
        success:handleFormSuccess,
        error: handleFormError
    })

})

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
})

$(document).ready(function() {
    converter = new showdown.Converter();
    converter.setFlavor('github');
    $('*[id*="-showdown"]').each(function() {
        const text = document.getElementById(this.id.slice(0, -9)).value;
        $(this).html(converter.makeHtml(text));
    });
})
