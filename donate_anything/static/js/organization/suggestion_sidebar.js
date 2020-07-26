const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#full-body-wrapper").toggleClass("toggled");
});

function add_to_sidebar(edit_id, username, edit, created, updated) {
    converter = new showdown.Converter();
    converter.setFlavor('github');
    let date;
    if (created === updated) {
        date = "Created: " + created;
    } else {
        date = "Updated: " + updated;
    }
    let canMarkRead = "";
    if ($("sidebar-body").attr("data-allow-read")) {
        canMarkRead = '<button class="btn btn-small" onclick="markRead(this,' + edit_id + ')">Mark Read</button>';
    }
    // escape texts
    username = document.createTextNode(username).wholeText;
    edit = document.createTextNode(edit).wholeText;

    let html = '<div class="list-group-item bg-light"><h4><a href="'+
        $("#sidebar-body").attr("data-username-url").replace("placeholder", username) +'">' +
        username + '</a></h4>' + canMarkRead +
        '<p class="font-italic font-weight-light">' + date + '</p><div>' +
        converter.makeHtml(edit) + '</div></div>';
    document.getElementById("sidebar-body").innerHTML += html;
}

function markRead(elem, edit_id) {
    let url = $("#sidebar-body").attr("data-mark-viewed-url").replace("0", edit_id);
    $.ajax({
        url: url,
        dataType: "json",
        type: "POST",
        success: function(_) {
            elem.parentNode.parentNode.removeChild(elem.parentNode);
        }
    });
}

function loadMore(unseen_only = true, page = "1") {
    let url = $("#sidebar-wrapper").attr("data-sidebar-url") + "?page=" + page;
    if (unseen_only) {
        url += "&unseen=1";
    }
    $.ajax({
        url: url,
        dataType: "json",
        type: "GET",
        success: function(data) {
            data = data["data"];
            for (let i=0; i < data.length; i++) {
                // edit_id, username, edit, created, updated
                add_to_sidebar(data[i][0], data[i][1], data[i][2], data[i][3], data[i][4]);
            }
        },
        fail: function(_) {
            let elem = document.getElementById("load-more-button");
            elem.parentNode.removeChild(elem);
        }
    });
}

function loadMoreButtonClick(elem) {
    const nextPage = elem.getAttribute("data-next-page");
    loadMore(true, nextPage);
    elem.setAttribute("data-next-page", parseInt(nextPage) + 1);
}

$(document).ready(function() {
    // Fill sidebar even if not opened
    loadMore(true, 1);
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
