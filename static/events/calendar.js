function evaluateTiles(){
    $(".calendar-tile").each(function (index, value) {
        let tile = $(value);
        tile.removeClass("focused-tile");
        $(`.${tile.attr("data-berks-dental-event-date")}`).css("display", "none");
    });
    $(this).addClass("focused-tile");
    $(`.${$(this).attr("data-berks-dental-event-date")}`).css("display", "grid");
}

$(document).ready(function () {
    let today = $(".calendar-today");
    let tiles = $(".calendar-tile");
    tiles.click(evaluateTiles);
    if (today.length === 0)
    {
        evaluateTiles.bind(tiles.first())();
    } else {
        today.click();
    }

});