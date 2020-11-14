const mediaURL = document.body.getAttribute("data-media-url");
const searchURL = document.body.getAttribute("data-search-url");
// handles item information. Item ID: [name, pic]
const cartKey = "itemCart";
// handles what items go to which charities. Charity ID: [item ID, 2, 3]
const charityCartKey = "charityCart";
// holds charity information to send less API calls. Charity ID: [...]
const charityDescKey = "charityDescKey";

/**
 * Adds an item to user's cart
 * @param item_id {number} item ID
 * @param name {string} name of item
 * @param pic {string, null} picture of item, if exists
 */
function addItem(item_id, name, pic) {
    let data = localStorage.getItem(cartKey);
    data = data === null ? {} : JSON.parse(data);
    // stringify to maintain compatibility to remove the need to parseInt
    data[item_id.toString()] = [name, pic];
    localStorage.setItem(cartKey, JSON.stringify(data));
}

/**
 * Adds a charity to user's cart
 * @param charity_id {number, string} Charity ID
 * @param item_id {number, string} Item ID to link to item cart
 * Optional parameters
 * @param charity_name {string, null} Charity name
 * @param charity_desc {string, null} Charity description
 * @param charity_how_to {string, null} Charity How To Donate
 * @param charity_logo {string, undefined/null} Charity's Logo
 */
function addCharity(
    charity_id,
    item_id,
    charity_name,
    charity_desc,
    charity_how_to,
    charity_logo,
) {
    let data = localStorage.getItem(charityCartKey);
    data = data === null ? {} : JSON.parse(data);
    let c_data = localStorage.getItem(charityDescKey);
    c_data = c_data === null ? {} : JSON.parse(c_data);
    // check if already in
    const c_string = charity_id.toString();
    if (data.hasOwnProperty(c_string)) {
        const item_id_string = item_id.toString();
        let manipulate = data[c_string];
        if (!(manipulate.includes(item_id_string))) {
            data[c_string].push(item_id_string);
        }
    } else {
        data[c_string] = [item_id.toString()];
        c_data[c_string] = {
            name: charity_name || "",
            description: charity_desc || "",
            how_to: charity_how_to || "",
        }
        if (charity_logo) {
            c_data[c_string]["logo"] = charity_logo;
        }
    }
    localStorage.setItem(charityCartKey, JSON.stringify(data));
    localStorage.setItem(charityDescKey, JSON.stringify(c_data))
}

/**
 * Removes an item from charity cart
 * @param charity_id {number, string} Charity ID
 * @param item_id {number, string} Item ID
 */
function removeItemFromCharity(charity_id, item_id) {
    let data = localStorage.getItem(charityCartKey);
    if (data === null) {
        localStorage.setItem(charityCartKey, JSON.stringify({}));
        return;
    }
    data = JSON.parse(data);
    const c_string = charity_id.toString();
    if (data.hasOwnProperty(c_string)) {
        let manipulate = data[c_string];
        const index = manipulate.indexOf(item_id.toString())
        if (index > -1) {
            manipulate.splice(index, 1);
            if (manipulate.length === 0) {
                delete data[c_string];
            } else {
                data[c_string] = manipulate;
            }
            localStorage.setItem(charityCartKey, JSON.stringify(data))
        }
    }
}

// API

/**
 * Gets the URL's query parameter
 * @param url {string} Use window.location.href
 * @returns {{}} Dictionary of query parameter and string value pair
 */
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
