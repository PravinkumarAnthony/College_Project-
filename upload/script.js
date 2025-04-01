const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const fileSelectBtn = document.getElementById('fileSelectBtn');
const fileNameDisplay = document.getElementById('fileName');
const resumeList = document.getElementById('resumeList');

// Load resumes on page load
window.onload = fetchResumes;

fileSelectBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    fileNameDisplay.textContent = `Selected: ${file.name}`;
    uploadFile(file);
  }
});

dropArea.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropArea.classList.add('dragover');
});

dropArea.addEventListener('dragleave', () => dropArea.classList.remove('dragover'));

dropArea.addEventListener('drop', (event) => {
  event.preventDefault();
  dropArea.classList.remove('dragover');
  const file = event.dataTransfer.files[0];
  if (file) uploadFile(file);
});

function uploadFile(file) {
  const formData = new FormData();
  formData.append('resume', file);

  console.log("Uploading file:", file.name); // See file name in console

  fetch('upload.php', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
      console.log("Server response:", data); // Log whole response to console

      if (data.status === 'success') {
        alert('Upload successful!');
        fetchResumes(); // Refresh list if successful
      } else {
        // Show specific error message
        alert('Upload failed: ' + data.message);
      }
    })
    .catch(err => {
      console.error('Fetch Error:', err); // Log fetch error
      alert('An unexpected error occurred. Check console for details.');
    });
}

function fetchResumes() {
  fetch('upload.php?action=list')
    .then(res => res.json())
    .then(data => {
      resumeList.innerHTML = '';
      data.forEach(item => {
        resumeList.innerHTML += `
          <li class="resume-item">
            <span class="file-name" title="${item.file_name}">${item.file_name}</span>
            <span class="action-buttons">
              <a href="${item.file_path}" download class="btn btn-download">Download</a>
              <button onclick="deleteResume(${item.id})" class="btn btn-delete">Delete</button>
            </span>
          </li>`;
      });
    });
}

function deleteResume(id) {
  if (confirm("Are you sure you want to delete this resume?")) {
    fetch('upload.php?action=delete&id=' + id, { method: 'GET' })
      .then(() => fetchResumes())
      .catch(err => alert('Delete failed.'));
  }
}
