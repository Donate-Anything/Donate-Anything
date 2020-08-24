// For editing-form of proposed items and
// paginating existing items of ProposedItem objects

let page = 1;
let currentScrollHeight = 0;
let lockScroll = false;

const _DATA_ID_SINGLE_STRING = "data-item-id"; // db proposed item obj id
const _DATA_IDS_LIST_STRING = "data-item-ids";
const _DATA_ITEM_CONDITION_ATTR = "data-item-condition";

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
                const conditionStringArray = [
                    "Poor Condition", "Used - Acceptable", "Used - Very Good", "Brand New"
                ];
                let existentTable = document.getElementById("existent-table");
                for (let i = 0; i < data["data"].length; i++) {
                    if (existentTable) {
                        let row = existentTable.insertRow(-1);
                        row.insertCell(0).innerText = data["data"][i][1];
                        // add condition
                        let condition = row.insertCell(1);
                        let selectNode = document.createElement("select");
                        selectNode.setAttribute("onchange", "existentSelectOnChange(this)");
                        selectNode.setAttribute(_DATA_ID_SINGLE_STRING, data["data"][i][0]);
                        const currentCondition = data["condition"][i];
                        for (let x of conditionStringArray) {
                            let option = document.createElement("option");
                            option.value = x;
                            option.text = x;
                            if (conditionStringArray.indexOf(x) === currentCondition) {
                                option.setAttribute("selected", "selected");
                            }
                            selectNode.appendChild(option);
                        }
                        condition.appendChild(selectNode);
                        // add remove
                        let remove = row.insertCell(2);
                        let aNode = document.createElement("a");
                        let textNode = document.createTextNode("Remove");
                        aNode.appendChild(textNode);
                        aNode.classList.add("text-danger");
                        aNode.setAttribute(_DATA_ID_SINGLE_STRING, data["data"][i][0]);
                        remove.appendChild(aNode)
                    } else {
                        let ul = document.getElementById("existent-list");
                        let li = document.createElement("li");
                        li.appendChild(document.createTextNode(data["data"][i][1] + " (" + conditionStringArray[data["condition"][i]] + ")"));
                        ul.appendChild(li);
                    }
                }
                page++
                if (!(data.has_next)) {
                    lockScroll = true;
                }
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
    let existingIDList = existingTable.getAttribute(_DATA_IDS_LIST_STRING).slice(1, -1).replace(/ /g,'');
    existingTable.setAttribute(_DATA_IDS_LIST_STRING, existingIDList);
    let existingCondition = existingTable.getAttribute(_DATA_ITEM_CONDITION_ATTR).slice(1, -1).replace(/ /g,'');
    existingTable.setAttribute(_DATA_ITEM_CONDITION_ATTR, existingCondition);
});

$(window).on("scroll", () => {
    paginateItem();
    // all ids are listed already
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

// Change item condition array
function existentSelectOnChange(elem) {
    const table = document.getElementById("existent-table")
    let conditionArray = Array.from(table.getAttribute(_DATA_ITEM_CONDITION_ATTR).split(","));
    let idArray = Array.from(table.getAttribute(_DATA_IDS_LIST_STRING).split(","));
    const index = idArray.indexOf(elem.getAttribute(_DATA_ID_SINGLE_STRING));
    conditionArray[index] = elem.selectedIndex;
    table.setAttribute(_DATA_ITEM_CONDITION_ATTR, conditionArray.toString());
}

function saveProgress(url) {
    // Assuming this isn't the first time...
    let existentTable = document.getElementById("existent-table");
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
            id: existentTable.getAttribute("data-obj-id"),
            item: existentTable.getAttribute(_DATA_IDS_LIST_STRING),
            item_condition: existentTable.getAttribute(_DATA_ITEM_CONDITION_ATTR),
            names: names.toString(),
            names_condition: names_condition.toString()
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

$("#existent-table").on("click", "tr a.text-danger", function(e) {
    e.preventDefault()
    let table = document.getElementById("existent-table");
    let existingIDList = table.getAttribute(_DATA_IDS_LIST_STRING).split(",").map(function(item) { return parseInt(item, 10)});
    const index = existingIDList.indexOf(parseInt($(this).attr(_DATA_ID_SINGLE_STRING), 10))
    if (index > -1) {
      existingIDList.splice(index, 1);
    }
    table.setAttribute(_DATA_IDS_LIST_STRING, existingIDList.toString());
    // delete condition
    let existingConditionList = Array.from(table.getAttribute(_DATA_ITEM_CONDITION_ATTR).split(","));
    if (index > -1) {
        existingConditionList.splice(index, 1);
    }
    table.setAttribute(_DATA_ITEM_CONDITION_ATTR, existingConditionList.toString());

    $(this).closest('tr').remove();
})
