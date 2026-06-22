// Patient Search
function searchPatient() {
    let input = document
        .getElementById("searchPatient")
        .value.toLowerCase();

    let rows = document
        .getElementById("patientTable")
        .getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        let name = rows[i].cells[1].innerText.toLowerCase();
        rows[i].style.display = name.includes(input) ? "" : "none";
    }
}

// Upload Prescription
function uploadPrescription() {
    let file = document.getElementById("fileUpload").files[0];

    if (file) {
        document.getElementById("uploadMsg").innerHTML =
            "Prescription Uploaded: " + file.name;
    } else {
        alert("Please select a file");
    }
}

// Book Appointment
function bookAppointment() {

    let name = document.getElementById("name").value;
    let date = document.getElementById("date").value;
    let reason = document.getElementById("reason").value;

    if (name === "" || date === "" || reason === "") {
        alert("Please fill all fields");
        return;
    }

    let table = document.getElementById("appointmentTable");

    let row = table.insertRow();

    row.innerHTML = `
        <td>${name}</td>
        <td>${date}</td>
        <td>${reason}</td>
        <td class="status-pending">Pending</td>
        <td>
            <button class="accept" onclick="approve(this)">
                Accept
            </button>

            <button class="reject" onclick="rejectAppointment(this)">
                Reject
            </button>
        </td>
    `;

    document.getElementById("message").innerHTML =
        "✅ Appointment Request Submitted Successfully";

    document.getElementById("name").value = "";
    document.getElementById("date").value = "";
    document.getElementById("reason").value = "";
}

// Accept Appointment
function approve(btn) {
    let row = btn.parentElement.parentElement;
    row.cells[3].innerHTML = "Accepted";
    row.cells[3].className = "status-accepted";
}

// Reject Appointment
function rejectAppointment(btn) {
    let row = btn.parentElement.parentElement;
    row.cells[3].innerHTML = "Rejected";
    row.cells[3].className = "status-rejected";
}