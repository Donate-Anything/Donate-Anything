const orgURL = document.getElementById("main").getAttribute("data-org-url").slice(0,-2);

/**
 * Sorts an array of key {number} with values of type array,
 * sort by longest array
 * @param data {Object} the object from charityCartKey
 * @return {(this|{})[]} list of data's keys, sorted,
 *                      with a dict num_items:[charity_id]
 */
function sortLongArray(data) {
    // since I'm an amateur at JS, here's a naive solution:
    // keys are length and values are [charity IDs]
    let ordered = {};
    let lengthsOrder = new Set();
    for (const key in data) {
        const length = data[key].length;
        if (ordered.hasOwnProperty(length)) {
            ordered[length].push(key);
        } else {
            ordered[length] = [key];
        }
        lengthsOrder.add(length);
    }
    // reorder set
    lengthsOrder = [...lengthsOrder].sort(function(a,b) {return b-a});
    return [lengthsOrder, ordered];
}

function blankCart() {
    const header = document.createElement("div");
    header.classList.add("text-center");
    const h2 = document.createElement("h2");
    h2.innerText = "Empty Cart";
    const description = document.createElement("p");
    description.innerText = "You can start adding items to your " +
        "cart by looking up what you can donate from the home page.";
    header.append(h2, description);
    document.getElementById("main").appendChild(header);
}

function ___start() {
    let data = localStorage.getItem(charityCartKey);
    let charityData = localStorage.getItem(charityDescKey);
    let itemData = localStorage.getItem(cartKey);
    if (data === null || charityData === null || itemData === null) {
        blankCart();
        return;
    }
    data = JSON.parse(data);
    charityData = JSON.parse(charityData);
    itemData = JSON.parse(itemData);
    let ordered = sortLongArray(data);
    const itemCharity = ordered[1];
    ordered = ordered[0];
    if (ordered.length === 0) {
        blankCart();
        return;
    }
    const targetDiv = document.getElementById("main");
    for (const length of ordered) {
        if (length === 0) continue;
        const header = document.createElement("h3");
        header.innerText = `${length} ${length === 1 ? "Item":"Items"}`
        targetDiv.appendChild(header);
        // Add Organizations to section
        for (let charity_id of itemCharity[length]) {
            const organizationDiv = document.createElement("div");
            // Add charity header
            const charity = charityData[charity_id.toString()];
            const headerLink = document.createElement("a");
            headerLink.href = `${orgURL}${charity_id}/`;
            const organizationHeader = document.createElement("div");
            // const organizationImg = document.createElement("img");
            // organizationImg.src = charity[1];
            const organizationTitle = document.createElement("h3");
            organizationTitle.innerText = charity.name;
            organizationHeader.append(organizationTitle);
            // Add items
            const itemList = document.createElement("ul");
            itemList.classList.add("list-unstyled");
            for (const item_id of data[charity_id.toString()]) {
                const liEl = document.createElement("li");
                const checkboxEl = document.createElement("input");
                checkboxEl.setAttribute("type", "checkbox");
                const textEl = document.createElement("p");
                textEl.innerText = itemData[item_id.toString()][0];
                textEl.classList.add("d-inline-block", "pl-2");
                liEl.append(checkboxEl, textEl);
                itemList.append(liEl);
            }
            organizationDiv.append(organizationHeader, itemList);
            targetDiv.appendChild(organizationDiv);
        }
    }
}

___start();
