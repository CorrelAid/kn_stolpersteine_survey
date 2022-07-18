$(document).ready(function () {
    $("#add_Familienangehörige").on('click', function() {
        if (($('#Familienangehörige .form-group-member').length == 1) && $('#Familienangehörige .form-group-member').is(":hidden")){
            $('#Familienangehörige .form-group-member').show()
            $('#Familienangehörige .form-group-member').attr('hidden',false);
        } else {
        $('#Familienangehörige .form-group-member:last').clone().insertAfter('#Familienangehörige .form-group-member:last')
        }
    })

    $("#Familienangehörige").on('click', "#delete_Familienangehörige", function(e) {
        e.preventDefault();
        if ($('#Familienangehörige .form-group-member').length == 1){
            $(this).closest('#Familienangehörige .form-group-member').hide();
            $(this).closest('#Familienangehörige .form-group-member').attr('hidden',true);
        } else {
            $(this).closest('#Familienangehörige .form-group-member').remove();
        }
    })

    $("#add_Stationen").on('click', function() {
        if (($('#Stationen  .form-group-member').length == 1) && $('#Stationen  .form-group-member').is(":hidden")){
            $('#Stationen  .form-group-member').show()
            $('#Stationen  .form-group-member').attr('hidden',false);
        } else {
        $('#Stationen  .form-group-member:last').clone().insertAfter('#Stationen  .form-group-member:last')
        }
    })

    $("#Stationen").on('click', "#delete_Stationen", function(e) {
        e.preventDefault();
        if ($('#Stationen .form-group-member').length == 1){
            $(this).closest('#Stationen .form-group-member').hide();
            $(this).closest('#Stationen .form-group-member').attr('hidden',true);
        } else {
            $(this).closest('#Stationen .form-group-member').remove();
        }
    })

    $("#add_Fluchtversuche").on('click', function() {
        if (($('#Fluchtversuche .form-group-member').length == 1) && $('#Fluchtversuche .form-group-member').is(":hidden")){
            $('#Fluchtversuche .form-group-member').show()
            $('#Fluchtversuche .form-group-member').attr('hidden',false);
        } else {
        $('#Fluchtversuche .form-group-member:last').clone().insertAfter('#Fluchtversuche .form-group-member:last')
        }
    })

    $("#Fluchtversuche").on('click', "#delete_Fluchtversuche", function(e) {
        e.preventDefault();
        if ($('#Fluchtversuche .form-group-member').length == 1){
            $(this).closest('#Fluchtversuche .form-group-member').hide();
            $(this).closest('#Fluchtversuche .form-group-member').attr('hidden',true);
        } else {
            $(this).closest('#Fluchtversuche .form-group-member').remove();
        }
    })

    function removeHidden(){
        $(".form-group-member:hidden").remove()
    }

});

