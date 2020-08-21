// Typeahead Search items for both initial and editing
// since we need to add (non)existing items to two tables

const typeAheadID = "#typeahead-input-field.tt-input";
const _itemDataIDs = "data-item-ids";
let selectedName = null;
let selectedID = null;

$('#typeahead-input-field').typeahead({
    minLength: 1,
    highlight: true
},
{
    limit: 15,
    async: true,
    display: "value",
    source: function(query, sync, asyncResults) {
        $.ajax({
            url: '/item/api/v1/item-autocomplete/',
            data: { "q": query.toLowerCase() },
            dataType: "json",
            type: "GET",
            success: function(data) {
                asyncResults($.map(data, function(item) {
                    let textArray = [];
                    for (let x of item) {
                        textArray.push({
                            id: x[0],
                            value: x[1],
                            imageURL: x[2]
                        });
                    }
                    return textArray
                }));
            }
        })
    },
    templates: {
        empty: [
            '<div id="">',
            "If you're seeing this, the item doesn't exist in the server. " +
            "Don't worry, we'll add it for you. Just hit enter or press \"Add Item\"",
            '</div>'
        ].join("\n"),
        suggestion: function(data) {
            const mediaURL = $("#main-scrollable-dropdown-menu").attr("django-media-url");
            let imageHTML = '';
            if (data.imageURL === mediaURL) {
                imageHTML = '<img style="height: 1em; width: 1em; float: left;" src="' +
                    mediaURL + data.imageURL + '">';
            }
            return '<div style="text-align: left">' + imageHTML + data.value + '</div>';
        }
    }
}
).bind("typeahead:select", function(ev, suggestion) {
    // item does exist in server db to be selected
    selectedName = suggestion.value;
    selectedID = suggestion.id;
}
).bind("typeahead:render", function(ev, suggestion, _async, _dataset) {
    const currentVal = $(typeAheadID).val();
    for (let nameDict of suggestion) {
        if (currentVal === nameDict.value) {
            selectedName = currentVal;
            selectedID = nameDict.id;
        } else {
            selectedName = null;
            selectedID = null;
        }
    }
}
).on("keydown", function(e) {
    if (e.which === 13 /* ENTER */) {
        const typeahead = $(this).data().ttTypeahead;
        const menu = typeahead.menu;
        const sel = menu.getActiveSelectable() || menu.getTopSelectable();
        if (menu.isOpen()) {
            if (sel === null) {
                // no suggestions
                addToTable();
                menu.close();
            } else {
                if (selectedName !== null) {
                    // if already matching
                    addToTable();
                    menu.close();
                } else {
                    // if not matching
                    menu.trigger('selectableClicked', sel);
                }
            }
            e.preventDefault();
        } else {
            addToTable();
        }
    }
})

function existentTableSelectChange(elem) {
    const table = document.getElementById("existent-table")
    let conditionArray = Array.from(table.getAttribute(_DATA_ITEM_CONDITION_ATTR).split(","));
    let idArray = Array.from(table.getAttribute(_DATA_IDS_LIST_STRING).split(","));
    const index = idArray.indexOf(elem.getAttribute(_DATA_ID_SINGLE_STRING))
    conditionArray[index] = elem.selectedIndex;
    table.setAttribute(_DATA_ITEM_CONDITION_ATTR, conditionArray.toString());
}

function addTableItem(tableID, item_id, name) {
    let table = document.getElementById(tableID);
    let row = table.insertRow(-1);
    row.insertCell(0).innerText = name;
    // Add condition dropdown
    let conditionRow = row.insertCell(1);
    let selectNode = document.createElement("select");
    if (tableID === "existent-table") {
        selectNode.setAttribute("onchange", "existentTableSelectChange(this)");
    }
    const conditionStringArray = [
        "Poor Condition", "Used - Acceptable", "Used - Very Good", "Brand New"
    ];
    const currentCondition = document.getElementById("current-select");
    for (let x of conditionStringArray) {
        let option = document.createElement("option");
        option.value = x;
        option.text = x;
        if (x === currentCondition.value) {
            option.setAttribute("selected", "selected");
            if (tableID === "existent-table") {
                let currentConditions = table.getAttribute("data-item-condition");
                if (currentConditions !== null && currentConditions !== "") {
                    currentConditions += ",";
                }
                currentConditions += currentCondition.selectedIndex;
                table.setAttribute("data-item-condition", currentConditions);
            }
        }
        selectNode.appendChild(option);
    }
    conditionRow.appendChild(selectNode);
    // Add remove
    let remove = row.insertCell(2);
    let aNode = document.createElement("a");
    let textNode = document.createTextNode("Remove");
    aNode.appendChild(textNode);
    aNode.classList.add("text-danger");
    if (item_id !== null) {
        // append new item ID to data
        let currentIDs = table.getAttribute(_itemDataIDs);
        if (currentIDs !== "") {
            currentIDs += ",";
        }
        table.setAttribute(_itemDataIDs, currentIDs + item_id);
        // finally set the attribute
        // yes, it's missing a single "s"
        aNode.setAttribute("data-item-id", item_id);
    }
    remove.appendChild(aNode)
}

function isDuplicateExistingID(string_item_id, clear_typeahead=true) {
    for (let x of Array.from(document.getElementById("existent-table").getAttribute(_itemDataIDs).split(","))) {
        if (x === string_item_id) {
            if (clear_typeahead) {
                $(typeAheadID).val("");
            }
            return true
        }
    }
    return false
}

function addItemChildrenToTable(item_id) {
    $.ajax({
        url: "/item/api/v1/item-children/" + item_id + "/",
        dataType: "json",
        type: "GET",
        success: function(data) {
            for (let item of data.data) {
                if (!(isDuplicateExistingID(item[0].toString(), false))) {
                    addTableItem("existent-table", item[0], item[1])
                }
            }
        }
    })
}

/// Adds item with ID to exist
function addToTable() {
    let typeahead = $(typeAheadID);
    let tableID, name;
    if (selectedID === null) {
        tableID = "non-existent-table";
        // selectedName would be null, as well
        name = typeahead.val();
        // Delete commas to prevent users from adding a list to one item
        name = name.replaceAll(",", "")
        // check no duplicates
        for (let x of $('#non-existent-table tr').find('td:first')) {
            if (x.innerText === name) {
                typeahead.val("");
                return
            }
        }
    } else {
        tableID = "existent-table";
        name = selectedName;
        // check no duplicates
        if (isDuplicateExistingID(selectedID.toString())) {
            return
        }
    }
    if (name === "") {
        // delete all of typeahead input in case someone just inputted a comma
        typeahead.val("");
        return
    }
    addTableItem(tableID, selectedID, name)
    // remove typeahead val
    $(typeAheadID).val("");
    // add item's children
    if (selectedID !== null) {
        addItemChildrenToTable(selectedID)
    }
}
