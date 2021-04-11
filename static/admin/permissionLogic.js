const dropDownConverter = {
    "Edit & View": "edit",
    "View": "view",
    "None": "none"
}

const jsonConverter = {
    "edit": "Edit & View",
    "view": "View",
    "none": "None"
}

function load_from_json(json) {
    let permissionObj = JSON.parse(json);
    $(".permDropdown").each(function (index, dropdown) {
        const viewset_name = dropdown.id.split("-")[0];
        if (viewset_name in permissionObj) {
            dropdown.value = jsonConverter[permissionObj[viewset_name]];
        }
    });
}

$(document).ready(() => {

    const perms_input = $("#id_permissions");
    load_from_json(perms_input.val());
    $(".form").submit(function (e) {
        let permissions = {};
        $(".permDropdown").each((index, dropdown) => {
            const viewset_name = dropdown.id.split("-")[0];
            permissions[viewset_name] = dropDownConverter[$(dropdown).find("option:selected").text()];
        });
        perms_input.val(JSON.stringify(permissions));
    });
});