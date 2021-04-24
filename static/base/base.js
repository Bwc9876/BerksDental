$(document).ready(function() {
    $(".nav-link").each(function (index, value) {
        value = $(value)
        if (document.title.endsWith(value.text())) {
            value.addClass("nav-link-current");
        }
    });
    $(".navbar-burger").click(function() {
        $(this).toggleClass("is-active");
        $(this).toggleClass("has-text-danger-dark");
        $(".navbar-menu").toggleClass("is-active");
    });
});