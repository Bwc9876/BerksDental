$(document).ready(function() {
    $(".nav-link").each(function (index, value) {
        value = $(value)
        if (document.title.endsWith(value.text())) {
            value.addClass("current");
        }
    });
    $(".nav-button").click(function() {
        let navLinkContainer = $(".nav-link-container");
        let pos = "150vw";
        if (!navLinkContainer.hasClass("show")) {
            navLinkContainer.scrollTop(0);
            pos = "0px";
        }
        navLinkContainer.toggleClass("show");
        $(".nav-link").each(function (index, value) {
            setTimeout(function() {
                $(value).css("left", pos);
            }, index*100);
        });
    });
});