function load_from_json(json) {
    let permissionObj = JSON.parse(json);
    $(".perm-dropdown").each(function (index, dropdown) {
        const viewset_name = dropdown.id.split("-")[0];
        if (viewset_name in permissionObj) {
            dropdown.value = permissionObj[viewset_name];
        }
    });
}

$(document).ready(() => {
    const perms_input = $("#id_permissions");
    load_from_json(perms_input.val());
    $(".form").submit(function () {
        let permissions = {};
        $(".perm-dropdown").each((index, dropdown) => {
            const viewset_name = dropdown.id.split("-")[0];
            permissions[viewset_name] = $(dropdown).find("option:selected").val();
        });
        perms_input.val(JSON.stringify(permissions));
    });
});