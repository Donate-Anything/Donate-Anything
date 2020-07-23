/* Project specific Javascript goes here. */
// Typeahead specific JS

// TODO Use cached results rather than always calling API.

const multiItemArrayKey = "multiItemArrayKey"
const multiItemStrArrayKey = "multiItemStrArrayKey"

function selectOne(id, value, page) {
    /* Get charities that support selected item
    * and fill them out in the template. */
    $.ajax({
        url: '/item/lookup/' + id + '/?page=' + page,
        dataType: "json",
        type: "GET",
        success: function(data) {
            // returned data is list_of(charity id, name, description[:150]) and has_next bool
            // TODO Maybe add branding description field? Kind of loses the lure though with people writing single line quotes.
            let html;
            if (page.toString() === "1") {
                html = ""
            } else {
                html = document.getElementById("organizations").innerHTML;
            }
            for (let x of data.data) {
                html += '<h3><a href="/organization/' +
                    x[0] + '/">' + x[1] + '</a></h3><p>' + x[2] + '</p>'
            }
            $('#organizations').html(html);
            let refresh = window.location.protocol + "//" + window.location.host + window.location.pathname +
                '?q=' + value + '&&page=' + page + '&&q_id=' + id + '';
            window.history.pushState({path: refresh}, 'Donate Anything', refresh)
            if (data.has_next) {
                $('#more-organizations-button').css("visibility", "visible");
            } else {
                $('#more-organizations-button').css("visibility", "hidden");
            }
        },
        fail: function(_) {
            // TODO Show as an error message
            console.log({"error": "Listed charities don't support this."});
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
      searchParams["page"]
  )
});

$("#search-multi-button").click(function() {
    let prefix = window.location.protocol + "//" + window.location.host + '/item/multi-lookup/?';
    let idArray = Array.from(localStorage.getItem(multiItemArrayKey).split(","));
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
    // For multi-items, we set attributes in localStorage for searching multi later on.
    localStorage.setItem(multiItemArrayKey, localStorage.getItem(multiItemArrayKey) + suggestion.id + ",")
    localStorage.setItem(multiItemStrArrayKey, localStorage.getItem(multiItemStrArrayKey) + suggestion.value + ",")
});

$(document).ready(function() {
    /* Allow for multiple input fields. Not all are Typeahead.
    * Only some because */
    let maxFields = 50;
    let inputWrapper = $("#main-scrollable-dropdown-menu");
    let addButton = $("#add-multi-button");
    const typeAheadID = "#typeahead-input-field.tt-input";

    // Set blank on page load if no items found
    let fieldCount = 1;
    let _idArray = localStorage.getItem(multiItemArrayKey);
    if (_idArray === null) {
        localStorage.setItem(multiItemArrayKey, "");
        localStorage.setItem(multiItemStrArrayKey, "");
    } else {
        // If found, then it was "go backwards"
        fieldCount = _idArray.length;
    }

    // add custom input box, not typeahead
    $(addButton).click(function(e) {
        e.preventDefault();
        if (fieldCount < maxFields) {
            fieldCount++;
            // Grab the typeahead input and insert into new custom random field.
            let typeaheadVal = $(typeAheadID).val();
            $(inputWrapper).append(
                '<div><input class="typeahead" readonly style="margin-bottom: 25px"' +
                ' value="' + typeaheadVal + '">' +
                '<a href="#" style="padding-left: 9px" class="delete-input">Delete</a></div>'
            );
            // Remove typeahead input.
            $(typeAheadID).val("");
            if (fieldCount === 1) {
                $('#search-multi-button').css('visibility', 'visible')
            }
        } else {
            alert('You can only search ' + maxFields + ' items at a time.')
        }
    });

    // remove custom input box, not typeahead input
    $(inputWrapper).on("click", ".delete-input", function(e) {
        e.preventDefault();
        // Remove item from arrays
        let nameArray = Array.from(localStorage.getItem(multiItemStrArrayKey).split(","));
        let idArray = Array.from(localStorage.getItem(multiItemArrayKey).split(","));
        const index = nameArray.indexOf($(this).siblings('.typeahead').val());
        if (index > -1) {
          localStorage.setItem(multiItemStrArrayKey, nameArray.splice(index, 1).toString());
          localStorage.setItem(multiItemArrayKey, idArray.splice(index, 1).toString());
        }

        // Remove element
        $(this).parent('div').remove();
        fieldCount--;
        if (fieldCount === 1) {
            $('#search-multi-button').css('visibility', 'hidden')
        }
    })
})
