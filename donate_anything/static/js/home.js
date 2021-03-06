/* Project specific Javascript goes here. */

// TODO Use cached results rather than always calling API.

const multiItemArrayKey = "multiItemArrayKey";
const multiItemStrArrayKey = "multiItemStrArrayKey";
const multiItemConditionArrayKey = "multiItemConditionArrayKey";
const maxFields = 100;
const typeAheadID = "#typeahead-input-field.tt-input";
const base_order = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-";
// if typeahead is not empty and was just selectOne'd
let isTypeaheadSelectOned = false;
// for scrolling to search results the first time
let hasShownSearch = false;
// if text in typeahead is being selected/highlighted
let isSelectHighlighting = false;

function base10_to_base64(num, condition="3") {
    num = parseInt(num.toString() + condition.toString());
    let str = "", r;
    while (num) {
        r = num % 64
        num -= r;
        num /= 64;
        str = base_order.charAt(r) + str;
    }
    return str;
}

function selectOne(id, value, condition_int_id, page, direct_link=false) {
    /* Get charities that support selected item
    * and fill them out in the template. */
    $.ajax({
        url: '/item/lookup/' + base10_to_base64(id, condition_int_id) + '/?page=' + page,
        dataType: "json",
        type: "GET",
        success: function(data) {
            // returned data is list_of(charity id, name, description[:150]) and has_next bool
            let html;
            const conditionStringArray = [
                "Poor Condition", "Used - Acceptable", "Used - Very Good", "Brand New"
            ];
            const condition = " (" + conditionStringArray[condition_int_id] + " or better)";
            if (page.toString() === "1") {
                if (data.data.length === 0) {
                    html = "<h4>No results for: " + value + condition + "</h4><hr>";
                } else {
                    html = "<h4>Showing organizations that accept: " + value + condition + "</h4><hr>"
                }
            } else {
                html = document.getElementById("organizations").innerHTML;
            }
            for (let x of data.data) {
                html += '<h3><a href="/organization/' +
                    x[0] + '/">' + x[1] + '</a></h3><p>' + x[2] + '</p>'
            }
            $('#organizations').html(html);
            isTypeaheadSelectOned = true;
            let refresh = window.location.protocol + "//" + window.location.host + window.location.pathname +
                '?q=' + value + '&page=' + page + '&q_id=' + id + '&condition=' + condition_int_id;
            window.history.pushState({path: refresh}, 'Donate Anything', refresh)
            if (data.has_next) {
                $('#more-organizations-button').css("visibility", "visible");
            } else {
                $('#more-organizations-button').css("visibility", "hidden");
            }
            if (direct_link) {
                $("#typeahead-input-field").typeahead("val", value);
                sessionStorage.setItem(multiItemArrayKey, id + ",");
                sessionStorage.setItem(multiItemStrArrayKey, value + ",");
                sessionStorage.setItem(multiItemConditionArrayKey, condition_int_id + ",");
                document.activeElement.blur();
                if (!hasShownSearch) {
                    window.scroll({
                        top: findPos(document.getElementById("organizations")),
                        behavior: 'smooth'
                    });
                    hasShownSearch = true;
                }
            }
        },
        fail: function(_) {
            $('#organizations').html("<h4 class='text-danger'>Listed charities don't supported this.</h4><hr>");
        }
    })
}

$("#more-organizations-button").click(function() {
  const searchParams = getParams(window.location.href);
  selectOne(
      searchParams["q_id"],
      searchParams["q"],
      parseInt(searchParams["condition"]),
      (parseInt(searchParams["page"], 10) + 1).toString()
  );
});

function findPos(obj) {
    let curtop = 0;
    if (obj.offsetParent) {
        do {
            curtop += obj.offsetTop;
        } while (obj === obj.offsetParent);
        return [curtop];
    }
}

function removeLast(q_name) {
    /* Since the typeahead value is always second-to last in the list
    * we only check that value. (Last is a space) */
    let nameArray = Array.from(sessionStorage.getItem(multiItemStrArrayKey).split(","));
    if (nameArray[nameArray.length - 2] === q_name) {
        let idArray = Array.from(sessionStorage.getItem(multiItemArrayKey).split(","));
        let conditionArray = Array.from(sessionStorage.getItem(multiItemConditionArrayKey).split(","));
        idArray.splice(-2); // deletes last space which gives the last comma
        idArray.push(""); // Adds a comma at the end
        nameArray.splice(-2);
        nameArray.push("");
        conditionArray.splice(-2);
        conditionArray.push("");
        sessionStorage.setItem(multiItemStrArrayKey, nameArray.toString());
        sessionStorage.setItem(multiItemArrayKey, idArray.toString());
        sessionStorage.setItem(multiItemConditionArrayKey, conditionArray.toString());
    }
}

$("#search-multi-button").click(function() {
    let prefix = window.location.protocol + "//" + window.location.host + '/item/multi-lookup/?';
    let idArray = Array.from(sessionStorage.getItem(multiItemArrayKey).split(","));
    let conditionArray = Array.from(sessionStorage.getItem(multiItemConditionArrayKey).split(","));
    for (let i = 0; i < idArray.length; i++) {
        const itemID = idArray[i];
        const cond = conditionArray[i];
        if (itemID === "") {
            continue
        }
        prefix += 'q=' + base10_to_base64(
            parseInt(itemID), cond
        ) + '&';
    }
    window.location.href = prefix + 'page=1'
})

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
          '<div>',
            "Try something more generic (e.g. pants instead of jeans) or filter by category",
          '</div>'
        ].join('\n'),
        suggestion: function (data) {
            if (window.location.pathname === "/") {
                // Show image only on landing page.
                // Top right search bar shouldn't show.
                const mediaURL = $("#home-container").attr("django-media-url");
                let imageHTML = '';
                if (data.imageURL === mediaURL) {
                    imageHTML = '<img style="height: 1em; width: 1em; float: left;" src="' +
                        mediaURL + data.imageURL + '">';
                }
                return '<div style="text-align: left">' + imageHTML + data.value + '</div>';
            } else {
                return '<div style="text-align: left">' + data.value + '</div>';
            }
        }
    }
}
).bind("typeahead:select", function(ev, suggestion) {
    const currentCondition = document.getElementById("current-select").selectedIndex;
    selectOne(suggestion.id, suggestion.value, currentCondition, 1);
    // For multi-items, we set attributes in sessionStorage for searching multi later on.
    // I really wish I knew about JSON.stringify before...
    sessionStorage.setItem(multiItemArrayKey, sessionStorage.getItem(multiItemArrayKey) + suggestion.id + ",");
    sessionStorage.setItem(multiItemStrArrayKey, sessionStorage.getItem(multiItemStrArrayKey) + suggestion.value + ",");
    sessionStorage.setItem(multiItemConditionArrayKey, sessionStorage.getItem(multiItemConditionArrayKey) + currentCondition + ",");
}
).on("keydown", function(e) {
    // $(this).val() will get the typeahead val before the keypress
    // https://github.com/twitter/typeahead.js/issues/332#issuecomment-379579385
    if (e.which === 13 /* ENTER */) {
        const typeahead = $(this).data().ttTypeahead;
        const menu = typeahead.menu;
        const sel = menu.getActiveSelectable() || menu.getTopSelectable();
        if (menu.isOpen()) {
            menu.trigger('selectableClicked', sel);
            document.activeElement.blur();
            if (!hasShownSearch) {
                window.scroll({
                    top: findPos(document.getElementById("organizations")),
                    behavior: 'smooth'
                });
                hasShownSearch = true;
            }
            e.preventDefault();
        }
    } else if (e.which === 8 /* Backspace */) {
        // This is mainly used if a user goes back and deletes typeahead value.
        removeLast($(this).val());
        isTypeaheadSelectOned = false;
    } else {
        /* FIXME If the user "selects all" with Ctrl A and types, the arrays are not updated
        * to account for the new typeahead value which replaced the "deleted"
        * typeahead value. */
        let q_name = getParams(window.location.href)["q"];
        if (isTypeaheadSelectOned && $(this).val() === q_name) {
            removeLast(q_name);
            isTypeaheadSelectOned = false;
        }
    }
});

$('input[type=search]').on('search', function () {
    const _typeahead = $(typeAheadID);
    if (_typeahead.val() === "" && isTypeaheadSelectOned) {
        // user pressed X button on Safari
        const params = getParams(window.location.href);
        removeLast(params["q"]);
        isTypeaheadSelectOned = false;
    }
    // else user searched for a suggestion that works
    // doesn't work if no suggestion appeared
})

function cantEditHomeAlert() {
    document.getElementById("cant-edit-alert").style.visibility = "visible";
    $("#cant-edit-alert").fadeTo(2000, 500).delay(3500).slideUp(500, function() {
        $("#cant-edit-alert").slideUp(500);
    });
}

function noValueHomeAlert() {
    document.getElementById("no-value-alert").style.visibility = "visible";
    $("#no-value-alert").fadeTo(2000, 500).delay(3500).slideUp(500, function() {
        $("#no-value-alert").slideUp(500);
    });
}

function searchOnConditionChange(elem) {
    const searchParams = getParams(window.location.href);
    const index = Array.from(sessionStorage.getItem(multiItemArrayKey).split(",")).indexOf(searchParams["q_id"]);
    const conditionArray = Array.from(sessionStorage.getItem(multiItemConditionArrayKey).split(","));
    if (index !== -1) {
        conditionArray[index] = elem.selectedIndex;
    }
    sessionStorage.setItem(multiItemConditionArrayKey, conditionArray.toString());

    selectOne(
        searchParams["q_id"],
        searchParams["q"],
        elem.selectedIndex,
        "1"
    );
}

$(document).ready(function() {
    // Hide so they don't take up space
    $("#cant-edit-alert").hide();
    $("#no-value-alert").hide();
    /* Allow for multiple input fields. Not all are Typeahead.
    * Only some because */
    let inputWrapper = $("#main-scrollable-dropdown-menu");
    let addButton = $("#add-multi-button");

    // Set blank on page load if no items found
    // If found, then it was "go backwards"
    // input has 2 typeahead classes
    let fieldCount = document.getElementsByClassName("typeahead").length - 1;
    if (sessionStorage.getItem(multiItemArrayKey) === null) {
        // initial page load
        // if you check web dev console, you won't see it, but the values
        // are there. They're not returning null but a blank string.
        sessionStorage.setItem(multiItemArrayKey, "");
        sessionStorage.setItem(multiItemStrArrayKey, "");
        sessionStorage.setItem(multiItemConditionArrayKey, "");
        $('#search-multi-button').hide();
        // For direct links to website
        const searchParams = getParams(window.location.href);
        if (searchParams["q_id"] && searchParams["q"] && searchParams["condition"]) {
            selectOne(
                searchParams["q_id"],
                searchParams["q"],
                searchParams["condition"],
                "1",
                true
            );
        } else if (searchParams["q"]) {
            // For search bar in Google
            const searchQuery = searchParams["q"];
            $("#typeahead-input-field").typeahead("val", searchQuery);
            $.ajax({
                url: '/item/api/v1/item-autocomplete/',
                data: { "q": searchQuery },
                dataType: "json",
                type: "GET",
                success: function(data) {
                    for (let returnedItem of data.data) {
                        if (returnedItem[1] === searchQuery) {
                            selectOne(returnedItem[0].toString(), returnedItem[1], 3, 1, true);
                            return;
                        }
                    }
                    document.getElementById("organizations").innerHTML =
                        "<h4>No results for: " + searchQuery + "</h4><hr>";
                    $('#more-organizations-button').css("visibility", "hidden");
                },
                fail: function() {
                    $('#organizations').html("<h4 class='text-danger'>Listed charities don't supported this.</h4><hr>")
                }
            })
        }
    } else if (fieldCount === 1 && $(typeAheadID).val() === "") {
        // refresh page of going back to home page via button
        sessionStorage.setItem(multiItemArrayKey, "");
        sessionStorage.setItem(multiItemStrArrayKey, "");
        sessionStorage.setItem(multiItemConditionArrayKey, "");
    }

    // add custom input box, not typeahead
    $(addButton).click(function(e) {
        e.preventDefault();
        // Grab the typeahead input and insert into new custom random field.
        let typeaheadVal = $(typeAheadID).val();
        if (typeaheadVal === "") {
            noValueHomeAlert()
        } else if (fieldCount < maxFields) {
            fieldCount++;
            $(inputWrapper).append(
                '<div><div><input class="typeahead" readonly style="margin-bottom: 25px"' +
                ' value="' + typeaheadVal + '" onclick="cantEditHomeAlert()">' +
                '<a href="#" style="padding-left: 9px" class="delete-input">Delete</a></div>' +
                '<div>Your ' + typeaheadVal + "'s condition: " +
                document.getElementById("current-select").value + '</div>'
            );
            // Remove typeahead input.
            $(typeAheadID).val("");
            isTypeaheadSelectOned = false;
            if (fieldCount > 1) {
                $('#search-multi-button').show();
            }
        } else {
            alert('You can only search ' + maxFields + ' items at a time.');
        }
    });

    // remove custom input box, not typeahead input
    $(inputWrapper).on("click", ".delete-input", function(e) {
        e.preventDefault();
        // Remove item from arrays
        let nameArray = Array.from(sessionStorage.getItem(multiItemStrArrayKey).split(","));
        let idArray = Array.from(sessionStorage.getItem(multiItemArrayKey).split(","));
        let conditionArray = Array.from(sessionStorage.getItem(multiItemConditionArrayKey).split(","));
        const index = nameArray.indexOf($(this).siblings('.typeahead').val());
        if (index > -1) {
            nameArray.splice(index, 1);
            idArray.splice(index, 1);
            conditionArray.splice(index, 1);
            sessionStorage.setItem(multiItemStrArrayKey, nameArray.toString());
            sessionStorage.setItem(multiItemArrayKey, idArray.toString());
            sessionStorage.setItem(multiItemConditionArrayKey, conditionArray.toString());
        }

        // Remove element
        $(this).parent('div').parent('div').remove();
        fieldCount--;
        if (fieldCount === 1) {
            $('#search-multi-button').hide();
        }
    })
})
