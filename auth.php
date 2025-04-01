<?php
session_start();
include "config.php";

$action = $_POST['action'];

function isValidUsername($username) {
    return preg_match('/^[a-zA-Z0-9_]{3,20}$/', $username);
}

function isValidPassword($password) {
    return preg_match('/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/', $password);
}

if ($action == "signup") {
    $username = $_POST['username'];
    $email = $_POST['email'];
    $password = $_POST['password'];

    if (!isValidUsername($username)) {
        echo "Invalid username format! Username must be 3-20 characters long and can only contain letters, numbers, and underscores.";
        exit();
    }

    if (!isValidPassword($password)) {
        echo "Invalid password format! Password must be at least 6 characters long and include at least one letter and one number.";
        exit();
    }

    $password = password_hash($password, PASSWORD_BCRYPT);

    $stmt = $conn->prepare("INSERT INTO users (username, email, password) VALUES (?, ?, ?)");
    $stmt->bind_param("sss", $username, $email, $password);
    if ($stmt->execute()) {
        echo "Signup Successful!";
    } else {
        echo "Error: " . $stmt->error;
    }
} 

elseif ($action == "login") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    if (!isValidUsername($username)) {
        echo "Invalid username format!";
        exit();
    }

    if (!isValidPassword($password)) {
        echo "Invalid password format!";
        exit();
    }

    $stmt = $conn->prepare("SELECT password FROM users WHERE username=?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $stmt->bind_result($hashed_password);
    $stmt->fetch();

    if (password_verify($password, $hashed_password)) {
        $_SESSION['user'] = $username;
        echo "Login Successful!";
        exit();
    } else {
        echo "Invalid Credentials!";
    }
} 

elseif ($action == "send_otp") {
    $email = $_POST['email'];
    $otp = rand(100000, 999999);

    $stmt = $conn->prepare("UPDATE users SET otp=? WHERE email=?");
    $stmt->bind_param("ss", $otp, $email);
    if ($stmt->execute()) {
        echo "OTP Sent! Your OTP is: " . $otp;  // Ideally, send OTP via email instead of displaying it
    } else {
        echo "Failed to send OTP!";
    }
    $stmt->close();
} 

elseif ($action == "reset_password") {
    $email = $_POST['email'];
    $otp = $_POST['otp'];
    $newPassword = $_POST['newPassword'];

    if (!isValidPassword($newPassword)) {
        echo "Invalid password format! Password must be at least 6 characters long and include at least one letter and one number.";
        exit();
    }

    $newPassword = password_hash($newPassword, PASSWORD_BCRYPT);

    $stmt = $conn->prepare("SELECT otp FROM users WHERE email=?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $stmt->bind_result($db_otp);
    $stmt->fetch();
    $stmt->close();

    if ($otp == $db_otp) {
        $stmt = $conn->prepare("UPDATE users SET password=?, otp=NULL WHERE email=?");
        $stmt->bind_param("ss", $newPassword, $email);
        if ($stmt->execute()) {
            echo "Password Reset Successful!";
        } else {
            echo "Error resetting password!";
        }
    } else {
        echo "Invalid OTP!";
    }
}
?>
