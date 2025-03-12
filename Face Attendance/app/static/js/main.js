// Initialize webcam when the page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.getElementById('webcam');
        video.srcObject = stream;
    } catch (err) {
        console.error('Error accessing webcam:', err);
        alert('Error accessing webcam. Please make sure you have granted camera permissions.');
    }
});

// Confetti animation function
function confetti({ particleCount = 100, spread = 70 }) {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff'];
    const container = document.querySelector('.container');
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'confetti-piece';
        particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 3 + 2) + 's';
        particle.style.opacity = Math.random();
        particle.style.transform = `rotate(${Math.random() * 360}deg)`;
        
        container.appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => particle.remove(), 5000);
    }
} 