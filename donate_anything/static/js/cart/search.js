const ___CURRENT_ITEM_ID = document.getElementById("listed-carts").getAttribute("data-item-id");
const REMOVE_TRANSLATE_TEXT = document.getElementById("listed-carts").getAttribute("data-remove-text");
const __TYPEAHEAD_ID = '#typeahead-input-field';
const ORGANIZATION_URL = document.getElementById("listed-added-cart").getAttribute("data-organization-url").slice(0,-2);

// if item catalogue is not in localStorage with search page
// then we can set it ourselves. This mostly happens if
// coming from Google or a bookmark
const urlParams = getParams(window.location.href);
addItem(urlParams["q_id"], urlParams["q"], null);

/**
 * Builds a "Remove from cart" button.
 * @param charity_id {number, string} Charity ID to remove item (current one of page)
 * @return {HTMLButtonElement}
 */
function buildRemoveButton(charity_id) {
    const removeButton = document.createElement("button");
    removeButton.classList.add("btn", "btn-danger", "d-inline-block", "px-3", "py-1");
    removeButton.innerText = REMOVE_TRANSLATE_TEXT;
    removeButton.addEventListener("click", function() {
        removeItemFromCharity(charity_id, ___CURRENT_ITEM_ID);
    })
    return removeButton;
}

document.getElementById("listed-carts")
    .querySelectorAll(".grow-charity-card")
    .forEach(function(el) {
        const charity_id = el.getAttribute("data-charity-id");
        el.querySelector(".btn-primary").addEventListener("click", function() {
            addCharity(
                charity_id,
                ___CURRENT_ITEM_ID,
                el.querySelector("h2").innerText,
                el.querySelector("p").innerText,
            )
            const removeButton = buildRemoveButton(charity_id);
            removeButton.addEventListener("click", function() {
                removeButton.parentNode.removeChild(removeButton);
            })
            this.parentNode.appendChild(removeButton);
        })
    }
);

$(__TYPEAHEAD_ID).typeahead({
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

// set search bar default
$(__TYPEAHEAD_ID).typeahead("val", urlParams["q"]).blur();

/**
 *
 * @param charity_id {number, string} Charity ID
 * @param name {string} Charity name
 * @param desc {string} Charity description
 * @return {HTMLDivElement} Charity card
 */
function createCharityCard(charity_id, name, desc) {
    const card = document.createElement("div");
    card.classList.add("grow-charity-card");
    card.style.flexShrink = "0";
    card.style.width = "350px";
    card.setAttribute("data-charity-id", charity_id);
    const header = document.createElement("h2");
    const link = document.createElement("a");
    link.href = `${ORGANIZATION_URL}${charity_id}/`;
    link.innerText = name;
    header.appendChild(link);
    // TODO Change this when implementing charity pictures
    const linkPic = document.createElement("a");
    linkPic.href = `${ORGANIZATION_URL}${charity_id}/`;

    const handHold = document.createElement("i");
    handHold.classList.add("fa", "fa-hand-holding-heart", "py-2");
    linkPic.appendChild(handHold);

    // Buttons
    const actionButtons = document.createElement("div");
    actionButtons.classList.add("add-cart", "col", "text-center");
    const removeButton = buildRemoveButton(charity_id);
    removeButton.addEventListener("click", function() {
        card.parentNode.removeChild(card);
    })
    actionButtons.append(removeButton);

    const description = document.createElement("p");
    description.innerText = desc;
    card.append(header, linkPic, actionButtons, description);
    return card;
}

function setupAlreadyAdded() {
    let data = localStorage.getItem(charityCartKey), c_data = localStorage.getItem(charityDescKey);
    if (data === null || c_data === null) return;
    data = JSON.parse(data);
    c_data = JSON.parse(c_data);
    // collect which charities the item is in
    let charitiesAdded = [];
    for (const charity_id in data) {
        if (data.hasOwnProperty(charity_id)) {
            if (data[charity_id].includes(___CURRENT_ITEM_ID)) {
                charitiesAdded.push(charity_id);
            }
        }
    }
    const listedAdded = document.getElementById("listed-added-cart");
    if (charitiesAdded.length === 0) return;
    const header = document.createElement("h3");
    header.innerText = `"${urlParams["q"]}" already added in:`
    $(`${header.outerHTML}<hr>`).insertBefore(listedAdded);
    $("<hr>").insertAfter(listedAdded);
    // Add to scrollable carousel
    for (const charity_id of charitiesAdded) {
        const charityInfo = c_data[charity_id]
        const build = createCharityCard(charity_id, charityInfo.name, charityInfo.description);
        build.classList.add("d-inline-block");
        listedAdded.appendChild(build);
    }
}
setupAlreadyAdded();
