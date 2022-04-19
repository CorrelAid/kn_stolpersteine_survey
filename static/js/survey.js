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
        if (($('.form-group-member').length == 1) && $('.form-group-member').is(":hidden")){
            $('.form-group-member:last').show()
            $('.form-group-member:last').attr('hidden',false);
        } else {
        $('.form-group-member:last').clone().insertAfter('.form-group-member:last')
        }
    })

    $("#Familie").on('click', "#delete_Familie", function(e) {
        e.preventDefault();
        if ($('.form-group-member').length == 1){
            $(this).closest('.form-group-member').hide();
            $(this).closest('.form-group-member').attr('hidden',true);
        } else {
            $(this).closest('.form-group-member').remove();
        }
    })


});

