document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');

    // Views
    const uploadView = document.getElementById('upload-view');
    const resultView = document.getElementById('result-view');
    const newScanBtn = document.getElementById('new-scan-btn');

    // Result Elements
    const resultBanner = document.getElementById('result-banner');
    const resultIconBg = document.getElementById('result-icon-bg');
    const resultIcon = document.getElementById('result-icon');
    const diagnosisLabel = document.getElementById('diagnosis-label');
    const diagnosisSubtext = document.getElementById('diagnosis-subtext');

    // Stats Elements
    const confidenceValueText = document.getElementById('confidence-value-text');
    const confidenceBarFill = document.getElementById('confidence-bar-fill');
    const processingTime = document.getElementById('processing-time');
    const detailTimestamp = document.getElementById('detail-timestamp');
    const reportTimestamp = document.getElementById('report-timestamp');

    let currentFile = null;

    // --- Drag and Drop Logic ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', function () {
        if (this.files.length) {
            handleFile(this.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.match('image.*')) {
            alert('Please upload an image file (PNG, JPG).');
            return;
        }

        currentFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewContainer.classList.remove('preview-hidden');
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = 'Analyze Image <i class="fa-solid fa-microscope" style="margin-left: 8px;"></i>';
        };
        reader.readAsDataURL(file);
    }

    // --- Analysis Logic ---
    analyzeBtn.addEventListener('click', () => {
        if (!currentFile) return;

        // UI Loading State (Upload View)
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...';
        previewContainer.classList.add('scanning-active');

        const formData = new FormData();
        formData.append('file', currentFile);

        // API Call
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                showResults(data);
            })
            .catch(err => {
                console.error(err);
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = 'Analyze Image';
                previewContainer.classList.remove('scanning-active');
                alert("Error: " + err.message);
            });
    });

    function showResults(data) {
        // Switch Views
        uploadView.classList.remove('active');
        resultView.classList.add('active');
        previewContainer.classList.remove('scanning-active');

        // Set Timestamps
        const now = new Date();
        const dateString = now.toLocaleDateString() + ', ' + now.toLocaleTimeString();
        reportTimestamp.textContent = `Generated: ${dateString}`;
        detailTimestamp.textContent = dateString;

        // Set Processing Time
        processingTime.textContent = (data.processing_time_ms / 1000).toFixed(2) + "s";

        // Determine state
        const isParasitized = data.label === "Parasitized";
        const themeColor = isParasitized ? 'var(--neon-red)' : 'var(--neon-green)';

        // Reset classes
        resultBanner.className = 'result-banner glass-panel';
        resultIconBg.className = 'result-icon-circle';

        if (isParasitized) {
            resultBanner.classList.add('state-parasitized');
            resultIconBg.classList.add('icon-parasitized');
            resultIcon.className = 'fa-solid fa-exclamation';
            diagnosisLabel.textContent = "PARASITIZED";
            diagnosisSubtext.textContent = "Malaria parasites detected";
        } else {
            resultIcon.className = 'fa-solid fa-check';
            diagnosisLabel.textContent = "UNINFECTED";
            diagnosisSubtext.textContent = "No malaria parasites detected";
        }

        // Animate Confidence Bar & Text
        const confPercent = (data.confidence * 100).toFixed(2);
        confidenceValueText.textContent = `${confPercent}%`;
        confidenceValueText.style.color = themeColor;

        // Start bar at 0 and transition to target
        confidenceBarFill.style.width = '0%';
        confidenceBarFill.style.backgroundColor = themeColor;

        setTimeout(() => {
            confidenceBarFill.style.width = `${confPercent}%`;
        }, 100);
        // Update logic for specific items
        if (data.scans_today !== undefined) {
            const scanDisplay = document.getElementById("scans-today-display");
            if (scanDisplay) {
                scanDisplay.textContent = data.scans_today.toLocaleString();
            }
        }
    }

    // --- Reset Logic ---
    newScanBtn.addEventListener('click', () => {
        resultView.classList.remove('active');
        uploadView.classList.add('active');

        previewContainer.classList.add('preview-hidden');
        previewContainer.classList.remove('scanning-active');
        imagePreview.src = '#';
        fileInput.value = '';
        currentFile = null;
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = 'Analyze Image';
    });
});
