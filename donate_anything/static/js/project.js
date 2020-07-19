/* Project specific Javascript goes here. */
// Typeahead specific JS

$('#search-box').typeahead({
    minLength: 1,
    highlight: true
},
{
    limit: 15,
    async: true,
    source: function(query, sync, asyncResults) {
        $.ajax({
            url: '/item/api/v1/item-autocomplete/',
            data: { "q": query.toLowerCase() },
            dataType: "json",
            type: "GET",
            success: function(data) {
                asyncResults($.map(data, function(item) {
                    return item
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
        // returned data is (item id, name, image url or non-null blank string)
        suggestion: function (data) {
            return '<div style="text-align: left">' +
                '<img style="height: 1em; width: 1em; float: left;" src="' +
                $("#search-form").attr("django-media-url") + data[2] + '">' +
                data[1] + '</div>';
        }
    }
}
).bind("typeahead:select", function(ev, suggestion) {
    $.ajax({
        url: '/item/lookup/' + suggestion[0] + '/',
        dataType: "json",
        type: "GET",
        success: function(data) {
            // returned data is list_of(charity id, name, description) and has_next bool
            console.log("Data: " + data.data);
            $(this).innerText = suggestion[1];
        }
    })
    // FIXME The text box shows the actual data with numbers. Should only show item name
}
).bind("typeahead:autocomplete", function(ev, suggestion) {
    // FIXME The text box shows the actual data with numbers. Should only show item name
});
