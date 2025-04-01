<?php
$host = "localhost"; // Change if needed
$db_name = "pixel_expert"; // Database name
$username = "root"; // DB username
$password = ""; // DB password

try {
    $conn = new PDO("mysql:host=$host;dbname=$db_name", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}
?>
