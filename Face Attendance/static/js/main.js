// main.js - Webcam control and attendance logic

// Webcam setup <button class="citation-flag" data-index="5"><button class="citation-flag" data-index="9">
const webcam = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        webcam.srcObject = stream;
        webcam.play();
        canvas.width = webcam.videoWidth;
        canvas.height = webcam.videoHeight;
    } catch (error) {
        alert('Error accessing webcam: ' + error.message);
    }
}

// Image capture for registration <button class="citation-flag" data-index="5"><button class="citation-flag" data-index="6">
function captureRegistrationPhoto() {
    ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// Attendance marking <button class="citation-flag" data-index="6"><button class="citation-flag" data-index="9">
async function markAttendance() {
    try {
        ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
        const photo = canvas.toDataURL('image/jpeg');
        
        const response = await fetch('/mark-attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `photo=${encodeURIComponent(photo)}`
        });
        
        const result = await response.json();
        if (result.success) {
            showConfetti();  // Celebration animation <button class="citation-flag" data-index="6">
            showStatus('success', result.success);
        } else {
            showStatus('error', result.error || 'Attendance failed');
        }
    } catch (error) {
        showStatus('error', 'Network error');
    }
}

// Confetti animation <button class="citation-flag" data-index="6">
function showConfetti() {
    // Add confetti elements to DOM
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti-piece';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.animationDelay = Math.random() * 2 + 's';
        document.body.appendChild(confetti);
    }
    setTimeout(() => {
        document.querySelectorAll('.confetti-piece').forEach(el => el.remove());
    }, 3000);
}

// Status display <button class="citation-flag" data-index="8">
function showStatus(type, message) {
    const statusBox = document.createElement('div');
    statusBox.className = `attendance-status ${type}`;
    statusBox.textContent = message;
    document.body.appendChild(statusBox);
    setTimeout(() => statusBox.remove(), 5000);
}

// Event listeners <button class="citation-flag" data-index="4">
document.addEventListener('DOMContentLoaded', () => {
    startWebcam();
    document.getElementById('registerBtn')?.addEventListener('click', () => {
        const photo = captureRegistrationPhoto();
        // Handle registration form submission
    });
});