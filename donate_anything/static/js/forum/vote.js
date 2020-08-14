$("#upvote").click(function(e) {
    let target = e.target;
    if (!(target.classList.contains("text-danger"))) {
        $.ajax({
            url: target.getAttribute("data-vote-url"),
            method: "POST",
            success: function() {
                target.classList.add("text-danger");
                $("#downvote").removeClass("text-danger");
                // Change texts
                let downE = document.getElementById("downvote-count");
                let upE = document.getElementById("upvote-count");
                upE.innerText = (parseInt(upE.innerText.split(" ")[0], 10) + 1).toString() + " upvotes"
                downE.innerText = (parseInt(downE.innerText.split(" ")[0], 10) - 1).toString() + " downvotes"
            },
        });
    }
})

$("#downvote").click(function(e) {
    let target = e.target;
    if (!(target.classList.contains("text-danger"))) {
        $.ajax({
            url: target.getAttribute("data-vote-url"),
            method: "POST",
            success: function() {
                target.classList.add("text-danger");
                $("#upvote").removeClass("text-danger");
                // Change texts
                let downE = document.getElementById("downvote-count");
                let upE = document.getElementById("upvote-count");
                downE.innerText = (parseInt(downE.innerText.split(" ")[0], 10) + 1).toString() + " downvotes"
                upE.innerText = (parseInt(upE.innerText.split(" ")[0], 10) - 1).toString() + " upvotes"
            },
        });
    }
})

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
        }
    }
})
