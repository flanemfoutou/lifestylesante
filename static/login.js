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
}

const csrftoken = getCookie('csrftoken');

const video = document.getElementById('video-element');
const image = document.getElementById('img-element');
const captureBtn = document.getElementById('capture-btn');
const reloadBtn = document.getElementById('reload-btn');

// Reload the page when the reload button is clicked
reloadBtn.addEventListener('click', () => {
    window.location.reload();
});

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

        const {height, width} = stream.getTracks()[0].getSettings();
        console.log(`Camera resolution: ${width}x${height}`);

        captureBtn.addEventListener('click', e => {
            e.preventDefault();
            captureBtn.classList.add('not-visible');
            const track = stream.getVideoTracks()[0];
            
            // Check if ImageCapture API is supported
            if ('ImageCapture' in window) {
                const imageCapture = new ImageCapture(track);
                console.log('ImageCapture API supported', imageCapture);

                imageCapture.takePhoto().then(blob => {
                    console.log("Took photo:", blob);

                    // Create an image element with the captured photo
                    const img = new Image(width, height);
                    img.src = URL.createObjectURL(blob);
                    image.append(img);

                    video.classList.add('not-visible');

                    const reader = new FileReader();
                    reader.readAsDataURL(blob);
                    reader.onloadend = () => {
                        const base64data = reader.result;
                        console.log(base64data);

                        const fd = new FormData();
                        fd.append('csrfmiddlewaretoken', csrftoken);
                        fd.append('photo', base64data);

                        // AJAX call to send the image to the server
                        $.ajax({
                            type: 'POST',
                            url: '/classify/',
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
                            }
                        });
                    };
                }).catch(error => {
                    console.log('takePhoto() error:', error);
                });
            } else {
                console.log("ImageCapture API not supported in this browser.");
            }
        });
    })
    .catch(error => {
        console.log("Error accessing camera:", error);
    });
} else {
    console.log("getUserMedia not supported in this browser.");
}
