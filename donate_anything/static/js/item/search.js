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
})

const _itemDataIDs = "data-item-ids";

/// Adds item with ID to exist
function addToTable() {
    let tableID, name;
    if (selectedID === null) {
        tableID = "non-existent-table";
        // selectedName would be null, as well
        name = $(typeAheadID).val();
    } else {
        tableID = "existent-table";
        name = selectedName;
    }
    let table = document.getElementById(tableID);
    let row = table.insertRow(-1);
    row.insertCell(0).innerText = name;
    let remove = row.insertCell(1);
    let aNode = document.createElement("a");
    let textNode = document.createTextNode("Remove");
    aNode.appendChild(textNode);
    aNode.classList.add("text-danger");

    if (selectedID !== null) {
        // append new item ID to data
        let currentIDs = table.getAttribute(_itemDataIDs);
        if (currentIDs !== "") {
            currentIDs += ",";
        }
        table.setAttribute(_itemDataIDs, currentIDs + selectedID);
        // finally set the attribute
        // yes, it's missing a single "s"
        aNode.setAttribute("data-item-id", selectedID);
    }
    remove.appendChild(aNode)
    // remove typeahead val
    $(typeAheadID).val("");
}
