<?php
require 'config.php';

header('Content-Type: application/json');

session_start();
$user = $_SESSION['user'];

function getUserId($conn, $username) {
    $stmt = $conn->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->execute([$username]);
    return $stmt->fetchColumn();
}

$method = $_SERVER['REQUEST_METHOD'];

switch ($method) {
    case 'POST':
        if (isset($_GET['action']) && $_GET['action'] == 'logout') {
            // Handle Logout
            session_destroy();
            header('Location: ../index.html'); // Redirect to login page
            exit();
        }

        // Handle File Upload
        if (isset($_FILES['resume'])) {
            $uploadDir = 'uploads/';
            if (!is_dir($uploadDir)) {
                mkdir($uploadDir, 0777, true);
            }

            $fileName = basename($_FILES['resume']['name']);
            $fileTmpName = $_FILES['resume']['tmp_name'];
            $fileSize = $_FILES['resume']['size'];
            $fileType = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));
            $allowedTypes = ['pdf', 'doc', 'docx'];

            if (!in_array($fileType, $allowedTypes)) {
                echo json_encode(['status' => 'error', 'message' => 'Only PDF, DOC, and DOCX files are allowed.']);
                exit();
            }

            if ($fileSize > 5 * 1024 * 1024) {
                echo json_encode(['status' => 'error', 'message' => 'File size should not exceed 5MB.']);
                exit();
            }

            $uniqueFileName = time() . '_' . $fileName;
            $filePath = $uploadDir . $uniqueFileName;

            if (move_uploaded_file($fileTmpName, $filePath)) {
                $userId = getUserId($conn, $user);
                $stmt = $conn->prepare("INSERT INTO resumes (user_id, file_name, file_path) VALUES (?, ?, ?)");
                $stmt->execute([$userId, $fileName, $filePath]);
                echo json_encode(['status' => 'success', 'message' => 'Resume uploaded successfully!']);
            } else {
                echo json_encode(['status' => 'error', 'message' => 'Failed to move uploaded file.']);
            }
        } else {
            echo json_encode(['status' => 'error', 'message' => 'No file uploaded.']);
        }
        break;

    case 'GET':
        if (isset($_GET['action']) && $_GET['action'] == 'list') {
            // List Resumes for the logged-in user
            $userId = getUserId($conn, $user);
            $stmt = $conn->prepare("SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_on DESC");
            $stmt->execute([$userId]);
            $resumes = $stmt->fetchAll(PDO::FETCH_ASSOC);
            echo json_encode($resumes);
        } elseif (isset($_GET['action']) && $_GET['action'] == 'delete' && isset($_GET['id'])) {
            // Delete Resume
            $id = $_GET['id'];
            $stmt = $conn->prepare("SELECT file_path FROM resumes WHERE id = ?");
            $stmt->execute([$id]);
            $file = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($file && file_exists($file['file_path'])) {
                unlink($file['file_path']); // Delete file
                $stmt = $conn->prepare("DELETE FROM resumes WHERE id = ?");
                $stmt->execute([$id]);
                echo json_encode(['status' => 'success', 'message' => 'File deleted.']);
            } else {
                echo json_encode(['status' => 'error', 'message' => 'File not found.']);
            }
        } else {
            echo json_encode(['status' => 'error', 'message' => 'Invalid request.']);
        }
        break;

    default:
        echo json_encode(['status' => 'error', 'message' => 'Unsupported request method.']);
        break;
}
?>
