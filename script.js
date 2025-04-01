$(document).ready(function () {
    // Switch to Signup Form
    $("#show-signup").click(function () {
        $("#login-section").hide();
        $("#signup-section").show();
    });

    // Switch to Login Form
    $("#show-login, #show-login2").click(function () {
        $("#signup-section, #forgot-section").hide();
        $("#login-section").show();
    });

    // Switch to Forgot Password Form
    $("#show-forgot").click(function () {
        $("#login-section").hide();
        $("#forgot-section").show();
    });

    // Function to clear form fields
    function clearForm(selector) {
        $(selector).find("input").val(""); // Clears all input fields
    }

    // Function to validate email format
    function isValidEmail(email) {
        let emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Function to validate password strength (at least 6 characters, one number, one letter)
    function isValidPassword(password) {
        let passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
        return passwordRegex.test(password);
    }

    // Handle Signup
    $("#signupBtn").click(function () {
        let username = $("#signup-username").val();
        let email = $("#signup-email").val();
        let password = $("#signup-password").val();
        let confirmPassword = $("#signup-confirm-password").val();

        if (!isValidEmail(email)) {
            alert("Invalid email format!");
            return;
        }
        if (!isValidPassword(password)) {
            alert("Password must be at least 6 characters long and include at least one letter and one number.");
            return;
        }
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        $.post("auth.php", { action: "signup", username, email, password }, function (response) {
            alert(response);
            clearForm("#signup-section"); // Clear form on success
        });
    });

    // Handle Login
    $("#loginBtn").click(function () {
        let username = $("#login-username").val();
        let password = $("#login-password").val();
    
        $.post("auth.php", { action: "login", username, password }, function (response) {
            alert(response.trim());
    
            if (response.trim() === "Login Successful!") {  
                clearForm("#login-section"); 
                window.location.href="upload/index.html";
            }
        });
    });
    
    // Handle Forgot Password - OTP Request
    $("#sendOtpBtn").click(function () {
        let email = $("#forgot-email").val();

        if (!isValidEmail(email)) {
            alert("Invalid email format!");
            return;
        }

        $.post("auth.php", { action: "send_otp", email }, function (response) {
            alert(response);
            $("#otp-section").show();
            clearForm("#forgot-section"); // Clear form on success
        });
    });

    // Handle Reset Password
    $("#resetPasswordBtn").click(function () {
        let email = $("#forgot-email").val();
        let otp = $("#otp").val();
        let newPassword = $("#new-password").val();
        let confirmNewPassword = $("#confirm-new-password").val();

        if (!isValidPassword(newPassword)) {
            alert("Password must be at least 6 characters long and include at least one letter and one number.");
            return;
        }
        if (newPassword !== confirmNewPassword) {
            alert("Passwords do not match!");
            return;
        }

        $.post("auth.php", { action: "reset_password", email, otp, newPassword }, function (response) {
            alert(response);
            clearForm("#forgot-section"); // Clear form on success
        });
    });
});
