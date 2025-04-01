USE pixel_expert;

CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_on DATETIME DEFAULT CURRENT_TIMESTAMP
);
