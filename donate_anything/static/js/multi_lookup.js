function convertToIntArray(stringArray) {
    return stringArray.split(',').map(Number)
}

$(document).ready(function() {
    // Remove duplicate IDs
    $('[id]').each(function() {
        $('[id="' + this.id + '"]:gt(0)').remove();
    });
    // Use session storage to grab ID of all assuming
    // the person came from a search

    const conditions = [
        "Poor Condition", "Used - Acceptable", "Used - Very Good", "Brand New"
    ];

    const itemIDArray = convertToIntArray(sessionStorage.getItem("multiItemArrayKey")).slice(0, -1);
    const itemNameArray = Array.from(sessionStorage.getItem("multiItemStrArrayKey").split(","));
    const conditionArray = convertToIntArray(sessionStorage.getItem("multiItemConditionArrayKey")).slice(0, -1);
    $('.item-data-treasure').each(function() {
        const orgItemData = convertToIntArray($(this).attr("data-item-ids").toString().slice(1,-1));
        let text = "Can fulfill: ";
        for (let itemID of orgItemData) {
            const itemIndex = itemIDArray.indexOf(itemID);
            text += itemNameArray[itemIndex] + " (" +
                conditions[conditionArray[itemIndex]] + "), "
        }
        // remove end comma
        $(this).text(text.slice(0, -2));
    })

    // TODO We should probably allow for bookmarks, but using localStorage can have negative consequences
})
