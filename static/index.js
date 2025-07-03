  function copyCode(button) {
    const codeBlock = button.closest(".code-block").querySelector("pre code");
    const code = codeBlock.innerText;

    navigator.clipboard.writeText(code).then(() => {
      button.textContent = "✅ Copied!";
      setTimeout(() => (button.textContent = "📋 Copy"), 1500);
    }).catch(err => {
      console.error("Copy failed:", err);
    });
  }


  function toggleDropdown() {
  const dropdown = document.getElementById('dropdownMenu');
  dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

function triggerFileUpload() {
  document.getElementById('fileUpload').click();
  toggleDropdown(); // Close dropdown after clicking
}

function uploadFile() {
  const fileInput = document.getElementById('fileUpload');
  if (fileInput.files.length > 0) {
    // Show loading indicator (optional)
    const submitBtn = document.querySelector('.submit-btn');
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Submit the form
    document.getElementById('uploadForm').submit();
  }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
  const dropdown = document.getElementById('dropdownMenu');
  const attachBtn = document.querySelector('.search-attach-btn');
  
  if (!attachBtn.contains(event.target) && !dropdown.contains(event.target)) {
    dropdown.style.display = 'none';
  }
});