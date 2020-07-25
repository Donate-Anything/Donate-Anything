// Code for viewing application and editing/suggesting

$(document).ready(function() {
    let converter = new showdown.Converter();
    converter.setFlavor('github');
    $("#org-description").html(converter.makeHtml(document.getElementById("org-description").innerHTML));
    $("#org-instructions").html(converter.makeHtml(document.getElementById("org-instructions").innerHTML));
    let legalDoc = document.getElementById("org-legal-doc");
    if (legalDoc) {
        legalDoc.innerHTML = converter.makeHtml(legalDoc.innerHTML);
    }
})
