function evaluateVirtual(){
    if ($("#id_virtual")[0].checked == true) {
        $("#Location_fieldset").toggleClass("hiddenField", true);
        $("#Link_fieldset").toggleClass("hiddenField", false);
    } else {
        $("#Location_fieldset").toggleClass("hiddenField", false);
        $("#Link_fieldset").toggleClass("hiddenField", true);
    }
}

$(document).ready(() => {

    evaluateVirtual();
    $("#id_virtual").change(evaluateVirtual);
    $("#id_startDate").change(() => {

        if ($("#id_endDate").val() == "") {
            $("#id_endDate").val($("#id_startDate").val());
        }

    });

});