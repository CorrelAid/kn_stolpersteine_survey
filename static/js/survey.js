$(document).ready(function () {
    function bindDelete(selector) {
        selector.on('click', function(e) {
            e.preventDefault();
            console.log("delete")
            if ($(this).parent().parent().parent().children('.form-group-member').length == 1){
                $(this).parent().parent().parent().children('.form-group-member').first().hide();
                $(this).parent().parent().parent().children('.form-group-member').first().attr('hidden',true);
            } else {
                $(this).parent().parent().remove();
            }
        });
    }

    function bindAdd(selector) {
        selector.on('click', function (e) {
            e.preventDefault();
            if (($(this).parent().children('.form-group-member').length == 1) && $(this).parent().children('.form-group-member').first().is(":hidden")) {
                $(this).parent().children('.form-group-member').first().show()
                $(this).parent().children('.form-group-member').first().attr('hidden', false);
            } else {
                $(this).parent().children('.form-group-member').last().clone().insertAfter($(this).parent().children('.form-group-member').last());
                bindDelete($(this).parent().children('.form-group-member').last().find(".delete_FormElement"));
                bindAdd($(this).parent().children('.form-group-member').last().find(".add_FormElement"));
            }
        });
    }

    // initial binding
    bindAdd($(".add_FormElement"));
    bindDelete($(".delete_FormElement"));

    function removeHidden(){
        $(".form-group-member:hidden").remove()
    }

});

