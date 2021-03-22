$(document).ready(function() {
    $(".nav-link").each(function (index, value) {
        value = $(value)
        if (document.title.endsWith(value.text())) {
            value.addClass("current");
        }
    });
    $(".nav-button").click(function() {
        let navLinkContainer = $(".nav-link-container");
        if (!navLinkContainer.hasClass("show")) {
            navLinkContainer.scrollTop(0);
        }
        navLinkContainer.toggleClass("show");
    });
});