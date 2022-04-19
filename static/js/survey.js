// TODO: function to add more elements in jquery (Stationen, family members)
$(document).ready(function () {
    // add family members
    let family_members = ["Vater", "Mutter", "Sohn", "Tochter", "Bruder", "Schwester", "Großmutter", "Großvater", "Enkelsohn", "Enkeltochter", "Onkel", "Tante", "Cousin", "Cousine", "Neffe", "Nichte", "Verlobte", "Ehefrau", "Ehemann", "Schwiegervater", "Schwiegermutter", "Schwiegersohn", "Schwiegertochter", "Schwager", "Schwägerin"];
    let selectFamilyMember = $(".Verwandschaftsbeziehung");
    for (var i = 0; i < family_members.length; i++) {
        let familyMemberElem = document.createElement("option");

        familyMemberElem.value = family_members[i];
        familyMemberElem.textContent = family_members[i];
        selectFamilyMember.append(familyMemberElem);
    }

    // add dates
    let selectDate = $(".datum");
    for (var i = 0; i < 32; i++) {
        let dateElement = document.createElement("option");

        dateElement.value = i;
        dateElement.textContent = i;
        selectDate.append(dateElement);
    }

    // add dates
    let months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
    let selectMonth = $(".monat");
    for (var i = 0; i < 13; i++) {
        let monthElement = document.createElement("option");

        monthElement.value = months[i];
        monthElement.textContent = months[i];
        selectMonth.append(monthElement);
    }

    // add years
    let selectYear = $(".jahr");
    for (var i = 1800; i < 2023; i++) {
        let yearElement = document.createElement("option");

        yearElement.value = i;
        yearElement.textContent = i;
        selectYear.append(yearElement);
    }


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
});

