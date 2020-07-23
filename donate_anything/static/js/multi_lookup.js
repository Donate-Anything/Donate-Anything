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

    const itemIDArray = convertToIntArray(sessionStorage.getItem("multiItemArrayKey")).slice(0, -1);
    const itemNameArray = Array.from(sessionStorage.getItem("multiItemStrArrayKey").split(","));
    $('.item-data-treasure').each(function() {
        const orgItemData = convertToIntArray($(this).attr("item-data").toString().slice(1,-1));
        let text = "Can fulfill: ";
        for (let itemID of orgItemData) {
            const itemIndex = itemIDArray.indexOf(itemID);
            text += itemNameArray[itemIndex] + ", "
        }
        $(this).text(text.slice(0, -2));
    })

    // TODO We should probably allow for bookmarks, but using localStorage can have negative consequences
})
