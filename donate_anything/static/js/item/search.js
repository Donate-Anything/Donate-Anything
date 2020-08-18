// Typeahead Search items for both initial and editing
// since we need to add (non)existing items to two tables

const typeAheadID = "#typeahead-input-field.tt-input";

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
            "Item doesn't exist in the server. We'll add it for you.",
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

const _itemDataIDs = "data-item-ids";

function addTableItem(tableID, item_id, name) {
    let table = document.getElementById(tableID);
    let row = table.insertRow(-1);
    row.insertCell(0).innerText = name;
    let remove = row.insertCell(1);
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
    for (let x of Array.from(document.getElementById("existent-table").getAttribute("data-item-ids").split(","))) {
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
