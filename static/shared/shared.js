$(document).ready(function() {
    $(".nav-button").click(function() {
        let navLinkContainer = $(".nav-link-container");
        if (!navLinkContainer.hasClass("show")) {
            navLinkContainer.scrollTop(0);
        }
        navLinkContainer.toggleClass("show");
    });
});