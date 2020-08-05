// For editing-form of proposed items and
// paginating existing items of ProposedItem objects

let page = 1;
let currentScrollHeight = 0;
let lockScroll = false;

const _DATA_ID_SINGLE_STRING = "data-item-id"

function paginateItem() {
    const scrollHeight = $(document).height();
    const scrollPos = Math.floor($(window).height() + $(window).scrollTop());
    const isBottom = scrollHeight - 350 < scrollPos;

    if (isBottom && currentScrollHeight < scrollHeight && !lockScroll) {
        $.ajax({
            url: $("#heading-with-data").attr("data-paging-url") + "?page=" + page,
            method: "GET",
            dataType: "json",
            success: function(data) {
                let existentTable = document.getElementById("existent-table");
                for (let item of data["data"]) {
                    if (existentTable) {
                        let row = existentTable.insertRow(-1);
                        row.insertCell(0).innerText = item[1];
                        let remove = row.insertCell(1);
                        let aNode = document.createElement("a");
                        let textNode = document.createTextNode("Remove");
                        aNode.appendChild(textNode);
                        aNode.classList.add("text-danger");
                        aNode.setAttribute(_DATA_ID_SINGLE_STRING, item[0]);
                        remove.appendChild(aNode)
                    } else {
                        let ul = document.getElementById("existent-list");
                        let li = document.createElement("li");
                        li.appendChild(document.createTextNode(item[1]));
                        ul.appendChild(li);
                    }
                }
                page++
            },
            error: function(_) {
                lockScroll = true;
                if (page === 1) {
                    let noneP = document.getElementById("none-item");
                    if (noneP) {
                        noneP.innerText = "The user didn't propose to add any server-existing items.";
                    }
                }
            }
        });
        currentScrollHeight = scrollHeight;
    }
}

$(document).ready(function() {
    $("#success-alert").hide();
    $("#fail-alert").hide();
    paginateItem();
    let existingTable = document.getElementById("existent-table");
    // remove square brackets
    let existingIDList = existingTable.getAttribute("data-item-ids").slice(1, -1).replace(/ /g,'');
    existingTable.setAttribute("data-item-ids", existingIDList);
});

$(window).on("scroll", () => {
    paginateItem();
    // all ids are listed already
});

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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

function saveProgress(url) {
    // Assuming this isn't the first time...
    let existentTable = document.getElementById("existent-table");
    $.ajax({
        url: url,
        method: "POST",
        data: {
            id: existentTable.getAttribute("data-obj-id"),
            item: existentTable.getAttribute("data-item-ids"),
            names: $('#non-existent-table tr').find('td:first').map(function() {
                 return $(this).text()
            }).get().toString()
        },
        success: function() {
            document.getElementById("success-alert").style.visibility = "visible";
            $("#success-alert").fadeTo(2000, 500).slideUp(500, function() {
              $("#success-alert").slideUp(500);
            });
        },
        error: function(xhr, status, error) {
            alert(xhr.responseText);
            document.getElementById("fail-alert").style.visibility = "visible";
            $("#fail-alert").fadeTo(2000, 500).slideUp(500, function() {
              $("#fail-alert").slideUp(500);
            });
        },
    })
}

$("#non-existent-table").on("click", "tr a.text-danger", function(e) {
    e.preventDefault()
    $(this).closest('tr').remove();
})

const _DATA_IDS_LIST_STRING = "data-item-ids";

$("#existent-table").on("click", "tr a.text-danger", function(e) {
    e.preventDefault()
    let table = document.getElementById("existent-table");
    let existingIDList = table.getAttribute(_DATA_IDS_LIST_STRING).split(",").map(function(item) { return parseInt(item, 10)});
    const index = existingIDList.indexOf(parseInt($(this).attr(_DATA_ID_SINGLE_STRING), 10))
    if (index > -1) {
      existingIDList.splice(index, 1);
    }
    table.setAttribute(_DATA_IDS_LIST_STRING, existingIDList.toString());

    $(this).closest('tr').remove();
})
