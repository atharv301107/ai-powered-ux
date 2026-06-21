document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const extractBtn = document.getElementById('extractBtn');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const fileName = document.getElementById('fileName');
    const removeBtn = document.getElementById('removeBtn');
    
    const emptyState = document.getElementById('emptyState');
    const loader = document.getElementById('loader');
    const progressText = document.getElementById('progressText');
    const resultContent = document.getElementById('resultContent');
    const ocrOutput = document.getElementById('ocrOutput');
    const copyBtn = document.getElementById('copyBtn');

    let selectedFile = null;

    // Trigger file browse when clicking drop zone
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & Drop visual effects
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        }, false);
    });

    // Handle File Drop
    dropZone.addEventListener('drop', (e) => {
        handleFiles(e.dataTransfer.files);
    });

    // Handle File Browse Input
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // File Validation & Handling
    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!allowedTypes.includes(file.type)) {
            alert('Invalid file type! Please upload a JPG, PNG, or WebP image.');
            return;
        }

        if (file.size > maxSize) {
            alert('File is too large! Maximum allowed size is 5MB.');
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => {
            imagePreview.src = reader.result;
            dropZone.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            extractBtn.disabled = false;
        };
    }

    // Remove Uploaded Image
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        imagePreview.src = '';
        selectedFile = null;
        previewContainer.classList.add('hidden');
        dropZone.classList.remove('hidden');
        extractBtn.disabled = true;
        resetResultState();
    });

    // Real OCR Processing using Tesseract.js
    extractBtn.addEventListener('click', () => {
        if (!selectedFile) return;

        // UI Transition
        emptyState.classList.add('hidden');
        resultContent.classList.add('hidden');
        loader.classList.remove('hidden');
        extractBtn.disabled = true;
        progressText.textContent = "Loading OCR Engine...";

        // Execute Real Text Extraction
        Tesseract.recognize(
            selectedFile,
            'eng',
            {
                logger: m => {
                    // Update user on loading state progress
                    if (m.status === 'recognizing text') {
                        progressText.textContent = `Analyzing text: ${Math.round(m.progress * 100)}%`;
                    }
                }
            }
        ).then(({ data: { text } }) => {
            loader.classList.add('hidden');
            resultContent.classList.remove('hidden');
            extractBtn.disabled = false;

            // Handle fallback if text cannot be found
            if (text.trim() === "") {
                ocrOutput.textContent = "OCR completed, but no text could be recognized in this image.";
            } else {
                ocrOutput.textContent = text;
            }
        }).catch(err => {
            console.error(err);
            loader.classList.add('hidden');
            extractBtn.disabled = false;
            alert("An error occurred during the OCR extraction processing.");
        });
    });

    // Copy to Clipboard Utility
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(ocrOutput.textContent).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = '#dcfce7';
            copyBtn.style.color = '#15803d';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '';
                copyBtn.style.color = '';
            }, 2000);
        });
    });

    function resetResultState() {
        emptyState.classList.remove('hidden');
        loader.classList.add('hidden');
        resultContent.classList.add('hidden');
        ocrOutput.textContent = '';
    }
});