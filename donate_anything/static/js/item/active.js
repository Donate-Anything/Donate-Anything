// JS file for showing the current items that an org can fulfill

let page = 1;
let currentScrollHeight = 0;
let lockScroll = false;

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
                    document.getElementById("items-list").innerHTML +=
                        "<li>" + x[0] + "<ul><li>Condition: " +
                        conditions[x[1]] + "</li></ul></li>"
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
});

$(window).on("scroll", () => {
    paginateItem();
});
