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
            const itemContainer = document.createElement('div');
            itemContainer.classList.add("text-left");
            if (data.imageURL !== "") {
                // Show image only on landing page.
                // Top right search bar shouldn't show.
                const itemImage = document.createElement("img");
                itemImage.style.cssText = "height: 1em; width: 1em; float: left;";
                if (data.imageURL.indexOf('http://') === 0 || data.imageURL.indexOf('https://') === 0) {
                    itemImage.src = data.imageURL;
                } else {
                    itemImage.src = `${mediaURL}${data.imageURL}`;
                }
                itemContainer.appendChild(itemImage);
            }
            const text = document.createElement("p");
            text.innerText = data.value;
            text.classList.add("d-inline-block", "pl-2");
            itemContainer.append(text);
            return itemContainer.outerHTML;
        }
    }
}
).bind("typeahead:select", function(ev, suggestion) {
    addItem(suggestion.id, suggestion.value, suggestion.imageURL);
    window.location.href = `${searchURL}?q=${suggestion.value}&q_id=${suggestion.id}`
}).on("keydown", function(e) {
    // $(this).val() will get the typeahead val before the keypress
    // https://github.com/twitter/typeahead.js/issues/332#issuecomment-379579385
    if (e.which === 13 /* ENTER */) {
        const typeahead = $(this).data().ttTypeahead;
        const menu = typeahead.menu;
        const sel = menu.getActiveSelectable() || menu.getTopSelectable();
        if (menu.isOpen()) {
            menu.trigger('selectableClicked', sel);
            document.activeElement.blur();
            e.preventDefault();
        }
    }
});
