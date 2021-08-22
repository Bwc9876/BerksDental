$(document).ready(() => {
    // noinspection JSUnresolvedFunction
    /**
     * This event handles three things
     * 1. Set up the sortable (drag & drop) on the sort_list element
     * 2. Set up the form to read the order of the items in the sort_list element and send it ot the backend
     * 3. If there are no items in the database, we disable the save button
     */
    // noinspection JSUnresolvedFunction
    $(".sort_list").sortable({
        'animation': 150,
        'ghostClass': "ghost-sort-target",
        'filter': ".empty-notification",
        'handle': ".handle"
    });
    if ($(".empty-notification").length === 0) {
        $(".form").submit(() => {
            let new_order = [];
            $(".sort-target").each((index, list_item) => {
                new_order.push($(list_item).attr("id"));
            });
            $("#id_new_order").val(new_order.join(","));
        });
    } else {
        $(".submit-button").prop("disabled", true);
    }
});