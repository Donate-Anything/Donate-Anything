// Form for initial proposal of new items for an organization

let _temp_org_id = null;
const _DATA_ID_SINGLE_STRING = "data-item-id"

$(document).ready(function() {
    $("#success-alert").hide();
    $("#fail-alert").hide();
    // Insert org name
    const _org_name_key = "temp_org_name"
    const org_name = sessionStorage.getItem(_org_name_key);
    if (org_name !== null) {
        $("#content-header").text("Propose Items to Merge with " + org_name);
    }
    const _temp_org_id_key = "temp_org_id";
    _temp_org_id = parseInt(sessionStorage.getItem(_temp_org_id_key), 10);
    if (_temp_org_id === null) {
        $("#content-header").text("Whoops, ERROR! Entity ID is missing! Please report this to staff.");
    }
    $("#existent-table").attr("data-obj-id", _temp_org_id);
    // change some anchor that requires the entity ID
    let currentActiveItemURLAnchor = $("#current-items-a-anchor");
    currentActiveItemURLAnchor.attr("href", currentActiveItemURLAnchor.attr("href").slice(0, -2) + _temp_org_id);
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

function saveProgress(url) {
    // Assuming this isn't the first time...
    let existentTable = document.getElementById("existent-table");
    let item_condition = [];
    for (let row of existentTable.rows) {
        if (row.cells[1].innerText === "Condition") {
            continue
        }
        item_condition.push(row.cells[1].children[0].selectedIndex);
    }
    let names = [];
    let names_condition = [];
    for (let row of document.getElementById("non-existent-table").rows) {
        if (row.cells[1].innerText === "Condition") {
            continue
        }
        names.push(row.cells[0].innerText);
        names_condition.push(row.cells[1].children[0].selectedIndex);
    }
    $.ajax({
        url: url,
        method: "POST",
        data: {
            entity: _temp_org_id,
            item: existentTable.getAttribute("data-item-ids"),
            item_condition: item_condition.toString(),
            names: names.toString(),
            names_condition: names_condition.toString()
        },
        success: function() {
            document.getElementById("success-alert").style.visibility = "visible";
            $("#success-alert").fadeTo(2000, 500).slideUp(500, function() {
              $("#success-alert").slideUp(500);
            });
            document.location.replace(existentTable.getAttribute("data-forum-url"));
        },
        error: function() {
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
