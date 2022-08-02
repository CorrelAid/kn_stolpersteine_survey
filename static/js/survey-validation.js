$(document).ready(function () {
    window.Parsley.addValidator('url', {
        validateString: function (value) {
            return value.toLowerCase().indexOf("html") === -1;
        },
        messages: {
            en: "The string cannot contain 'html'!",
            de: "Bitte 'html' entfernen."
        }
    });

    window.Parsley.addValidator('str', {
        validateString: function (value) {
            return ("str." in value.toLowerCase() &  "strasse" in value.toLowerCase());
        },
        messages: {
            en: "Please write 'str' as 'straße",
            de: 'Bitte nicht kürzen. Bitte ..straße statt ..strasse oder ..str. verwenden.'
        }
    });

    window.Parsley.addValidator('capsLock', {
        validateString: function (value) {
            return value.toUpperCase().indexOf("html") !== value;
        },
        messages: {
            en: "Please do not capitalize the whole string!",
            de: "Bitte nicht alles mit Großbuchstaben schreiben."
        }
    });
});