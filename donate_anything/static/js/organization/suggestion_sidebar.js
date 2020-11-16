$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#full-body-wrapper").toggleClass("toggled");
});

function add_to_sidebar(edit_id, username, edit, created, updated) {
    const sidebarBody = document.getElementById("sidebar-body");

    const header = document.createElement("h4");
    header.classList.add("list-group-item", "bg-light");
    const link = document.createElement("a");
    link.href = document.createTextNode(sidebarBody.getAttribute("data-username-url").replace("placeholder", username));
    link.innerText = document.createTextNode(username).wholeText;
    header.appendChild(link);
    sidebarBody.appendChild(header);
    
    if (sidebarBody.hasAttribute("data-allow-read")) {
        const markReadButton = document.createElement("button");
        markReadButton.classList.add("btn", "btn-small");
        markReadButton.addEventListener("click", function() {
            markRead(this, edit_id);
        });
        markReadButton.innerText = "Mark Read";
        sidebarBody.appendChild(markReadButton);
    }
    
    const editP = document.createElement("p");
    editP.classList.add("font-italic", "font-weight-light");
    editP.innerText = created === updated ? `Created: ${created}` : `Updated: ${updated}`;
    const editDiv = document.createElement("div");
    const converter = new showdown.Converter();
    converter.setFlavor("github");
    editDiv.innerHtml = converter.makeHtml(document.createTextNode(edit).wholeText);
    sidebarBody.append(editP, editDiv);
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
        error: function(_) {
            let elem = document.getElementById("load-more-button");
            elem.parentNode.removeChild(elem);
            console.log("End of suggestion sidebar")
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
            xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
        }
    }
})
