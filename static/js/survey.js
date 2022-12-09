$(document).ready(function () {
    function bindDelete(selector) {
        selector.on('click', function(e) {
            e.preventDefault();
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
            var parent_class = this

            if (($(parent_class).parent().children('.form-group-member').length == 1) && $(parent_class).parent().children('.form-group-member').first().is(":hidden")) {
                $(parent_class).parent().children('.form-group-member').first().show()
                $(parent_class).parent().children('.form-group-member').first().attr('hidden', false);
            } else {
                $(parent_class).parent().children('.form-group-member').last().clone().insertAfter($(parent_class).parent().children('.form-group-member').last());

                // clear dropdowns
                $(parent_class).parent().children('.form-group-member').last().find('select').each(function() { this.selectedIndex = 0 });
                // clear text
                $(parent_class).parent().children('.form-group-member').last().find('input[type=text]').each(function() { $(this).val(""); });
                // clear checkbox
                $(parent_class).parent().children('.form-group-member').last().find('input[type=checkbox]').each(function() { $(this).removeAttr('checked'); });

                bindDelete($(parent_class).parent().children('.form-group-member').last().find(".delete_FormElement"));
                bindAdd($(parent_class).parent().children('.form-group-member').last().find(".add_FormElement"));
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

