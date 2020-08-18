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
            url: '/organization/api/v1/org-autocomplete/',
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
            return '<div style="text-align: left">' + data.value + '</div>';
        }
    }
}
).bind("typeahead:select", function(ev, suggestion) {
    window.location.href = "/organization/" + suggestion.id;
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
    }
});
