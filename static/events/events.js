function getEvents(calendar_tile) {
    let events = [];
    calendar_tile.children(".eventJSON").each((index, child) => {
        events.push(JSON.parse($(child).text()));
    });
    return events;
}

function getDate(calendar_tile) {
    let date = undefined;
    $(calendar_tile).children(".dateText").each((index, child) => {
        date =  $(child).text();
    });
    return date;
}

$(document).ready(function () {
    $(".calendar-tile").click(function () {
        console.log(getEvents($(this)));
        if ($(this).hasClass("out-of-month") || $(this).hasClass("calendar-weekday")) {
            return;
        }
        $(".calendar-tile").each(function (index, value) {
            $(value).removeClass("focused-tile");
        });
        $(this).addClass("focused-tile");
        let events = getEvents($(this));
        let eventsToday = (events.length !== 0);
        $(".front-event-card").each(function (index, value) {
            if (index === 0) { return; }
            $(value).detach();
        });
        $("#event-list-title").text(eventsToday? "Events on " + events[0]["startDate"] : "There are no events that day.");
        for (let i = events.length-1; i >= 0; i--) {
            let event = events[i];
            let sameDay = (event["startDate"] === event["endDate"]);
            let eventCard = `<div class="front-event-card">
        <h2>${event["name"]}${sameDay?"":" Starts"}</h2>
        <p class="h4">${sameDay?`${event["startTime"]} - ${event["endTime"]}`:event["startTime"]}</p>
        <p class="h4">${event["virtual"]?`<a href="${event["link"]}">${event["link"]}</a>`:event["location"]}</p>
        <p class="event-front-description h4">${event["description"]}</p>
    </div>`;
            $(".event-cards-calendar").append(eventCard);
        }
    });
    $(".calendar-today").click();
});