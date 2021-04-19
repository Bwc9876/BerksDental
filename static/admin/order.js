$(document).ready(() => {
    /**
     * This event handles three things
     * 1. Setup the sortable (drag & drop) on the sort_list element
     * 2. Setup the form to read the order of the items in the sort_list element and send it ot the backend
     * 3. If there's no items in the database, we disable the save button
     */

    $(".sort_list").sortable({
        'animation': 150,
        'ghostClass': "ghostSortTarget",
        'filter': ".emptyNotification",
        'handle': ".handle"
    });

    if ($(".emptyNotification").length === 0) {

        $(".form").submit(() => {
            let new_order = [];
            $(".sortTarget").each((index, list_item) => {

                new_order.push($(list_item).attr("id"));

            });

            $("#id_new_order").val(new_order.join(","));
            console.log(new_order);

        });

    } else {

        $(".submit-button").prop("disabled", true);

    }

});