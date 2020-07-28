$("textarea").on('input', function () {
    // Check if it's the actual textarea
    // Ignore if it's just showdown itself
    if (this.id.slice(this.id.length - 9) !== "-showdown") {
        converter = new showdown.Converter();
        converter.setFlavor('github');
        const text = $(this).val(),
            target = document.getElementById(this.id.toString().concat("-showdown"));
        target.innerHTML = converter.makeHtml(text);
    }
})

$(document).ready(function() {
    converter = new showdown.Converter();
    converter.setFlavor('github');
    $('*[id*="-showdown"]').each(function() {
        const text = document.getElementById(this.id.slice(0, -9)).value;
        $(this).html(converter.makeHtml(text));
    });
})
