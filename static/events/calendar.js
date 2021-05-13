$(document).ready(function () {
    $(".calendar-tile").click(function () {
        $(".calendar-tile").each(function (index, value) {
            let tile = $(value);
            tile.removeClass("focused-tile");
            $(`.${tile.attr("data-berks-dental-event-date")}`).css("display", "none");
        });
        $(this).addClass("focused-tile");
        $(`.${$(this).attr("data-berks-dental-event-date")}`).css("display", "grid");
    });
    $(".calendar-today").click();
});