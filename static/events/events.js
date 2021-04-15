function getEvents(calendar_tile) {

    let events = [];
    $(calendar_tile).children(".event").each((index, child) => {

        events.push(JSON.parse($(child).text()));

    });
    return events;

}

$(document).ready(function () {
    $(".calendar-tile").click(function () {
        if ($(this).hasClass("out-of-month") || $(this).hasClass("calendar-weekday")) {
            return;
        }
        $(".calendar-tile").each(function (index, value) {
            $(value).removeClass("focused-tile");
        });
        $(this).addClass("focused-tile");
        console.log(getEvents(this));
    });
});