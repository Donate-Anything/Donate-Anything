$("#upvote").click(function(e) {
    let target = e.target;
    if (!(target.classList.contains("text-danger"))) {
        $.ajax({
            url: target.getAttribute("data-vote-url"),
            method: "POST",
            success: function() {
                target.classList.add("text-danger");
                let downVoteTick = $("#downvote");
                if (downVoteTick.hasClass("text-danger")) {
                    downVoteTick.removeClass("text-danger");
                    let downE = document.getElementById("downvote-count");
                    downE.innerText = (parseInt(downE.innerText.split(" ")[0], 10) - 1).toString() + " downvotes";
                }
                // Change texts
                let upE = document.getElementById("upvote-count");
                upE.innerText = (parseInt(upE.innerText.split(" ")[0], 10) + 1).toString() + " upvotes";
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
                let upvoteTick = $("#upvote");
                if (upvoteTick.hasClass("text-danger")) {
                    upvoteTick.removeClass("text-danger");
                    let upE = document.getElementById("upvote-count");
                    upE.innerText = (parseInt(upE.innerText.split(" ")[0], 10) - 1).toString() + " upvotes";
                }
                // Change texts
                let downE = document.getElementById("downvote-count");
                downE.innerText = (parseInt(downE.innerText.split(" ")[0], 10) + 1).toString() + " downvotes";
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
