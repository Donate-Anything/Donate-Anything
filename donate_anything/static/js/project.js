/* Project specific Javascript goes here. */
// Typeahead specific JS

// TODO Use cached results rather than always calling API.

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
                    for (let i = 0; i < item.length; i++) {
                        textArray.push({
                            id: item[i][0],
                            value: item[i][1],
                            imageURL: item[i][2]
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
                console.log(data)
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
    $.ajax({
        url: '/item/lookup/' + suggestion.id + '/',
        dataType: "json",
        type: "GET",
        success: function(data) {
            // returned data is list_of(charity id, name, description) and has_next bool
            console.log(data);
        }
    })
});
