$(document).ready(function () {
    let tiles = $(".in-month");
    let today = $(".is-today");
    let selected = today.length === 0 ? tiles.first() : today;
    tiles.click(function() {
        tiles.each(function (index, value) {
            let tile = $(value);
            let id = tile.attr("data-berks-dental-event-date");
            tile.removeClass("is-selected");
            if (id !== undefined && id !== "") {
                $(`.${id}`).each(function (index, value) {
                    $(value).removeClass("is-selected");
                });
            }
        });
        $(this).addClass("is-selected");
        let id = $(this).attr("data-berks-dental-event-date")
        $(`.${id}`).each(function (index, value) {
            $(value).addClass("is-selected");
        });
    });
    selected.click();
});