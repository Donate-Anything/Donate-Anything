$(document).ready(function() {
    let converter = new showdown.Converter();
    converter.setFlavor('github');
    const elements = document.querySelectorAll('.markdown-marker');
    Array.from(elements).forEach((element, _) => {
        element.innerHTML = converter.makeHtml(element.innerHTML);
    });
})
