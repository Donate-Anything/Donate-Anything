// JS file for showing the current items that an org can fulfill

let page = 1;
let currentScrollHeight = 0;
let lockScroll = false;
let canDelete = false;
let deleteURL = "";

function deleteWantedItem(elem) {
    const itemID = elem.getAttribute("data-item-id");
    $.ajax({
        url: deleteURL + itemID + "/",
        method: "POST",
        dataType: "text",
        success: function (_) {
            // button clicked
            let listItem = elem.parentNode.parentNode.parentNode;
            listItem.parentNode.removeChild(listItem);
        }
    })
}

function paginateItem() {
    const scrollHeight = $(document).height();
    const scrollPos = Math.floor($(window).height() + $(window).scrollTop());
    const isBottom = scrollHeight - 350 < scrollPos;

    const conditions = [
        "Poor Condition", "Used - Acceptable", "Used - Very Good", "Brand New"
    ];

    if (isBottom && currentScrollHeight < scrollHeight && !lockScroll) {
        $.ajax({
            url: $("#heading-with-data").attr("data-paging-url") + "?page=" + page,
            method: "GET",
            dataType: "json",
            success: function(data) {
                for (let x of data["data"]) {
                    if (canDelete) {
                        document.getElementById("items-list").innerHTML +=
                            "<li>" + x[0] + "<ul><li>Condition: " +
                            conditions[x[1]] + "</li><li>" +
                            "<button data-item-id=\"" + x[2] + "\" onclick=\"deleteWantedItem(this)\"" +
                            " style=\"background-color:transparent\" class=\"text-danger btn\">Delete</button></li></ul></li>"
                    } else {
                        document.getElementById("items-list").innerHTML +=
                            "<li>" + x[0] + "<ul><li>Condition: " +
                            conditions[x[1]] + "</li></ul></li>"
                    }
                }
                page++
                lockScroll = !(data["has_next"]);
            },
            error: function(_) {
                lockScroll = true;
                if (page === 1) {
                    document.getElementById("items-list").innerHTML +=
                        "<p>This organization may not have listed which items are fulfilled, yet.</p>"
                }
            }
        });
        currentScrollHeight = scrollHeight;
    }
}

$(document).ready(function() {
    paginateItem();
    const _itemList = document.getElementById("items-list");
    canDelete = _itemList.getAttribute("data-can-delete") === "True";
    deleteURL = _itemList.getAttribute("data-delete-url").slice(0, -2);
});

$(window).on("scroll", () => {
    paginateItem();
});

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
