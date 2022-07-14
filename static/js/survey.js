$(document).ready(function () {
    $("#add_Familie").on('click', function() {
        if (($('#Familie .form-group-member').length == 1) && $('#Familie .form-group-member').is(":hidden")){
            $('#Familie .form-group-member').show()
            $('#Familie .form-group-member').attr('hidden',false);
        } else {
        $('#Familie .form-group-member:last').clone().insertAfter('#Familie .form-group-member:last')
        }
    })

    $("#Familie").on('click', "#delete_Familie", function(e) {
        e.preventDefault();
        if ($('#Familie .form-group-member').length == 1){
            $(this).closest('#Familie .form-group-member').hide();
            $(this).closest('#Familie .form-group-member').attr('hidden',true);
        } else {
            $(this).closest('#Familie .form-group-member').remove();
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

    $("#add_Flucht").on('click', function() {
        if (($('#Flucht .form-group-member').length == 1) && $('#Flucht .form-group-member').is(":hidden")){
            $('#Flucht .form-group-member').show()
            $('#Flucht .form-group-member').attr('hidden',false);
        } else {
        $('#Flucht .form-group-member:last').clone().insertAfter('#Flucht .form-group-member:last')
        }
    })

    $("#Flucht").on('click', "#delete_Flucht", function(e) {
        e.preventDefault();
        if ($('#Flucht .form-group-member').length == 1){
            $(this).closest('#Flucht .form-group-member').hide();
            $(this).closest('#Flucht .form-group-member').attr('hidden',true);
        } else {
            $(this).closest('#Flucht .form-group-member').remove();
        }
    })

    function removeHidden(){
        $(".form-group-member:hidden").remove()
    }

});

