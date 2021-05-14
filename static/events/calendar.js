$(document).ready(function () {
    let tiles = $(".calendar-tile");
    let today = $(".calendar-today");
    let focused = today.length === 0 ? tiles.first() : today;
    tiles.click(function() {
        tiles.each(function (index, value) {
            let tile = $(value);
            let id = tile.attr("data-berks-dental-event-date")
            tile.removeClass("focused-tile");
            $(`.${id}`).css("display", "none");
        });
        $(this).addClass("focused-tile");
        let id = $(this).attr("data-berks-dental-event-date")
        $(`.${id}`).each(function (index, value) {
            let element = $(value);
            let setType = element.prop("tagName") === "P" ? "initial" : "grid";
            element.css("display", setType);
        });
    });
    focused.click();
});