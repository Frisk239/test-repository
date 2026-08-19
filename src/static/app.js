(function () {
    var form = document.getElementById("login-form");
    var username = document.getElementById("username");
    var password = document.getElementById("password");
    var errorEl = document.getElementById("form-error");

    form.addEventListener("submit", function (event) {
        var message = "";

        if (username.value.trim() === "" && password.value.trim() === "") {
            message = "Please enter your username and password.";
        } else if (username.value.trim() === "") {
            message = "Please enter your username.";
        } else if (password.value === "") {
            message = "Please enter your password.";
        }

        if (message !== "") {
            event.preventDefault();
            errorEl.textContent = message;
            errorEl.hidden = false;
            return;
        }

        event.preventDefault();
        errorEl.hidden = true;
        window.location.href = "/dashboard";
    });
})();