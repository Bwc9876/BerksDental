$(document).ready(function () {
    $(".event-card").click(function () {
        if($(this).hasClass("last-event-card")) {
            return;
        }
        let hadClass = $(this).hasClass("focused-event-card");
        $(".event-card").each(function (index, value) {
            $(value).removeClass("focused-event-card");
        });
        if (!hadClass) {
            $(this).addClass("focused-event-card");
        }
    });
});