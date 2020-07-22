/* Project specific Javascript goes here. */
// Typeahead specific JS

// TODO Use cached results rather than always calling API.


function selectOneInitial(id) {
    /* Get charities that support selected item
    * and fill them out in the template. */
    $.ajax({
        url: '/item/lookup/' + id + '/',
        dataType: "json",
        type: "GET",
        success: function(data) {
            // returned data is list_of(charity id, name, description[:150]) and has_next bool
            // TODO Maybe add branding description field? Kind of loses the lure though with people writing single line quotes.
            let html = ""
            for (let x of data.data) {
                html += '<h3><a href="/organization/' +
                    x[0] + '/">' + x[1] + '</a></h3><p>' + x[2] + '</p>'
            }
            $('#organizations').html(html);
            let refresh = window.location.protocol + "//" + window.location.host + window.location.pathname + '?page=1';
            window.history.pushState({path: refresh}, '', refresh)
        },
        fail: function(_) {
            // TODO Show as an error message
            console.log({"error": "Listed charities don't support this."});
        }
    })
}

$('#search-box').typeahead({
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
                    let textArray = [];  // Ref: https://twitter.github.io/typeahead.js/data/films/post_1960.json
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
                return '<div style="text-align: left">' +
                '<img style="height: 1em; width: 1em; float: left;" src="' +
                $("#search-form").attr("django-media-url") + data.imageURL + '">' +
                data.value + '</div>';
            } else {
                return '<div style="text-align: left">' + data + '</div>';
            }
        }
    }
}
).bind("typeahead:select", function(ev, suggestion) {
    selectOneInitial(suggestion.id);
});
