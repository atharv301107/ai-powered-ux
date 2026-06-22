// JavaScript behaviors for Epic 7: Health Prediction & Analytics
// Maintained by Sanskar Atpadkar

document.addEventListener("DOMContentLoaded", function() {
    console.log("Epic 7: Health Prediction & Analytics framework loaded and live.");
});

function executeEpicAction(endpoint, dataPayload) {
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataPayload)
    })
    .then(response => response.json())
    .then(data => {
        alert("Response status: " + data.status + "\nMessage: " + (data.message || data.reply || data.extracted_text || JSON.stringify(data)));
    })
    .catch(error => console.error('Error executing module callback:', error));
}