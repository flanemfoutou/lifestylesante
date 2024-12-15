console.log('hello world');

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

const csrftoken = getCookie('csrftoken');

const video = document.getElementById('video-element');
const scanBtn = document.getElementById('scan-btn');
const reloadBtn = document.getElementById('reload-btn');
const messageDiv = document.getElementById('message');

// Reload the page when the reload button is clicked
reloadBtn.addEventListener('click', () => {
    window.location.reload();
});

// Initialize QR code scanner
if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }
    })
    .then((stream) => {
        // Set the video source to the stream
        video.srcObject = stream;
        video.play();

        console.log("Camera streaming initialized");

        scanBtn.addEventListener('click', (e) => {
            e.preventDefault();
            scanBtn.classList.add('not-visible');

            // Use Html5Qrcode to scan QR codes
            const html5QrCode = new Html5Qrcode("video-element");

            html5QrCode.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: 250 },
                (decodedText) => {
                    // QR Code detected
                    console.log("QR Code detected:", decodedText);

                    const fd = new FormData();
                    fd.append('csrfmiddlewaretoken', csrftoken);
                    fd.append('qr_data', decodedText);

                    // AJAX call to send the QR data to the server
                    $.ajax({
                        type: 'POST',
                        url: '/login/',
                        enctype: 'multipart/form-data',
                        data: fd,
                        processData: false,
                        contentType: false,
                        success: (resp) => {
                            console.log(resp);
                            window.location.href = window.location.origin;
                        },
                        error: (err) => {
                            console.log(err);
                            alert("Erreur de connexion. Veuillez réessayer.");
                        }
                    });
                },
                (error) => {
                    console.warn("QR Code scan error:", error);
                    messageDiv.innerHTML = `<p class="error">Impossible de lire le QR Code. Essayez encore.</p>`;
                }
            ).catch(err => {
                console.error("Error initializing QR scanner:", err);
            });
        });
    })
    .catch(error => {
        console.log("Error accessing camera:", error);
        alert("Erreur : impossible d'accéder à la caméra.");
    });
} else {
    console.log("getUserMedia not supported in this browser.");
    alert("Votre navigateur ne prend pas en charge l'utilisation de la caméra.");
}
