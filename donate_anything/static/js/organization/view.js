$(document).ready(function() {
    // animate on scroll
    AOS.init();
    // show markdown
    let converter = new showdown.Converter();
    converter.setFlavor('github');
    $("#org-description").html(converter.makeHtml(document.getElementById("org-description").innerHTML));
    $("#org-instructions").html(converter.makeHtml(document.getElementById("org-instructions").innerHTML));
})

function goToProposeItemForm() {
    let contentHeader = document.getElementById("content-header");
    sessionStorage.setItem("temp_org_id", contentHeader.getAttribute("data-org-id"));
    sessionStorage.setItem("temp_org_name", contentHeader.innerText);
}
