$(document).ready(function () {
    $(".calendar-tile").click(function () {
        if($(this).hasClass("out-of-month")||$(this).hasClass("calendar-weekday")) {
            return;
        }
        $(".calendar-tile").each(function (index, value) {
            $(value).removeClass("focused-tile");
        });
        $(this).addClass("focused-tile");
    });
});