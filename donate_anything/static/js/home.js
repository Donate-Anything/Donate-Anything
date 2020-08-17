/* Project specific Javascript goes here. */

// TODO Use cached results rather than always calling API.

const multiItemArrayKey = "multiItemArrayKey"
const multiItemStrArrayKey = "multiItemStrArrayKey"
const maxFields = 50;
const typeAheadID = "#typeahead-input-field.tt-input";

function selectOne(id, value, page, direct_link=false) {
    /* Get charities that support selected item
    * and fill them out in the template. */
    $.ajax({
        url: '/item/lookup/' + id + '/?page=' + page,
        dataType: "json",
        type: "GET",
        success: function(data) {
            // returned data is list_of(charity id, name, description[:150]) and has_next bool
            let html;
            if (page.toString() === "1") {
                if (data.data.length === 0) {
                    html = "<h4>No results for: " + value + "</h4><hr>";
                } else {
                    html = "<h4>Showing organizations that accept: " + value + "</h4><hr>"
                }
            } else {
                html = document.getElementById("organizations").innerHTML;
            }
            for (let x of data.data) {
                html += '<h3><a href="/organization/' +
                    x[0] + '/">' + x[1] + '</a></h3><p>' + x[2] + '</p>'
            }
            $('#organizations').html(html);
            let refresh = window.location.protocol + "//" + window.location.host + window.location.pathname +
                '?q=' + value + '&page=' + page + '&q_id=' + id + '';
            window.history.pushState({path: refresh}, 'Donate Anything', refresh)
            if (data.has_next) {
                $('#more-organizations-button').css("visibility", "visible");
            } else {
                $('#more-organizations-button').css("visibility", "hidden");
            }
            if (direct_link) {
                $(typeAheadID).val(value);
            }
        },
        fail: function(_) {
            $('#organizations').html("<h4 class='text-danger'>Listed charities don't supported this.</h4><hr>");
        }
    })
}

const getParams = function (url) {
    let params = {};
    const parser = document.createElement('a');
    parser.href = url;
    const query = parser.search.substring(1);
    const vars = query.split('&');
    for (let i = 0; i < vars.length; i++) {
        const pair = vars[i].split('=');
        params[pair[0]] = decodeURIComponent(pair[1]);
    }
    return params;
};

$("#more-organizations-button").click(function() {
  const searchParams = getParams(window.location.href);
  selectOne(
      searchParams["q_id"],
      searchParams["q"],
      (parseInt(searchParams["page"], 10) + 1).toString()
  );
});

$("#search-multi-button").click(function() {
    let prefix = window.location.protocol + "//" + window.location.host + '/item/multi-lookup/?';
    let idArray = Array.from(sessionStorage.getItem(multiItemArrayKey).split(","));
    for (let x of idArray) {
        if (x === "") {
            continue
        }
        prefix += 'q=' + x + '&'
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
                const mediaURL = $("#main-scrollable-dropdown-menu").attr("django-media-url");
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
    selectOne(suggestion.id, suggestion.value, 1);
    // For multi-items, we set attributes in sessionStorage for searching multi later on.
    // I really wish I knew about JSON.stringify before...
    sessionStorage.setItem(multiItemArrayKey, sessionStorage.getItem(multiItemArrayKey) + suggestion.id + ",")
    sessionStorage.setItem(multiItemStrArrayKey, sessionStorage.getItem(multiItemStrArrayKey) + suggestion.value + ",")
}
).on("keydown", function(e) {
    // https://github.com/twitter/typeahead.js/issues/332#issuecomment-379579385
    if (e.which === 13 /* ENTER */) {
        const typeahead = $(this).data().ttTypeahead;
        const menu = typeahead.menu;
        const sel = menu.getActiveSelectable() || menu.getTopSelectable();
        if (menu.isOpen()) {
            menu.trigger('selectableClicked', sel);
            e.preventDefault();
        }
    } else if (e.which === 8 /* Backspace pressed */) {
        /* This is mainly used if a user goes back and deletes typeahead value.
        Since the typeahead value is always second-to last in the list
        we only check that value. (Last is a space) */
        let nameArray = Array.from(sessionStorage.getItem(multiItemStrArrayKey).split(","));
        if (nameArray[nameArray.length - 2] === $(this).val()) {
            let idArray = Array.from(sessionStorage.getItem(multiItemArrayKey).split(","));
            idArray.splice(-2); // deletes last space which gives the last comma
            idArray.push(""); // Adds a comma at the end
            nameArray.splice(-2);
            nameArray.push("");
            sessionStorage.setItem(multiItemStrArrayKey, nameArray.toString());
            sessionStorage.setItem(multiItemArrayKey, idArray.toString());
        }
    }
});

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
    let fieldCount = inputWrapper.length;
    if (fieldCount === 1 && $(typeAheadID).val() === "") {
        // initial page load
        sessionStorage.setItem(multiItemArrayKey, "");
        sessionStorage.setItem(multiItemStrArrayKey, "");
        $('#search-multi-button').hide();
        // For direct links to website
        const searchParams = getParams(window.location.href);
        if (searchParams["q_id"] && searchParams["q"]) {
            selectOne(
                searchParams["q_id"],
                searchParams["q"],
                "1",
                true
            );
        } else if (searchParams["q"]) {
            // For search bar in Google
            const searchQuery = searchParams["q"];
            $(typeAheadID).val(searchQuery);
            $.ajax({
                url: '/item/api/v1/item-autocomplete/',
                data: { "q": searchQuery },
                dataType: "json",
                type: "GET",
                success: function(data) {
                    // id, value, item image
                    for (let returnedItem of data.data) {
                        if (returnedItem[1] === searchQuery) {
                            selectOne(returnedItem[0].toString(), returnedItem[1], 1);
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
                '<div><input class="typeahead" readonly style="margin-bottom: 25px"' +
                ' value="' + typeaheadVal + '" onclick="cantEditHomeAlert()">' +
                '<a href="#" style="padding-left: 9px" class="delete-input">Delete</a></div>'
            );
            // Remove typeahead input.
            $(typeAheadID).val("");
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
        const index = nameArray.indexOf($(this).siblings('.typeahead').val());
        if (index > -1) {
            nameArray.splice(index, 1);
            idArray.splice(index, 1)
            sessionStorage.setItem(multiItemStrArrayKey, nameArray.toString());
            sessionStorage.setItem(multiItemArrayKey, idArray.toString());
        }

        // Remove element
        $(this).parent('div').remove();
        fieldCount--;
        if (fieldCount === 1) {
            $('#search-multi-button').hide();
        }
    })
})
