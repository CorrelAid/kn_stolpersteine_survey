// From Bootstrap documentation: https://getbootstrap.com/docs/5.0/forms/validation/
// TODO: could be nice to add some of these, although a lot of fields might not need validation now
// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
    'use strict';

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation()
                }

                form.classList.add('was-validated')
            }, false)
        })
})();