$(document).ready(function () {
    $(".nav-link").each(function (index, value) {
        value = $(value)
        if (document.title.endsWith(value.text())) {
            value.addClass("current-nav-link");
        }
    });
    $(".nav-button").click(function () {
        const body = $("body");
        body.toggleClass("menu-shown");
        $(".nav-button").text(body.hasClass("menu-shown")? "Close": "Menu")
        let navLinkContainer = $(".nav-link-container");
        navLinkContainer.scrollTop(0);
        navLinkContainer.toggleClass("menu-shown");
        $(".nav-link").each(function (index, value) {
            setTimeout(function () {
                $(value).toggleClass("menu-shown");
            }, index * 100);
        });
    });
});