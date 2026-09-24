function loadStudents() {
    fetch("/api/students")
        .then(response => response.json())
        .then(students => {
            displayStudents(students);
        })
        .catch(error => {
            console.error("Error loading student records:", error);
        });
}

function displayStudents(students) {
    const tableBody = document.getElementById("studentTableBody");
    const noRecords = document.getElementById("noRecords");

    tableBody.innerHTML = "";

    if (students.length === 0) {
        noRecords.style.display = "block";
        return;
    }

    noRecords.style.display = "none";

    students.forEach(student => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${student.id}</td>
            <td>${student.name}</td>
            <td>${student.usn}</td>
            <td>${student.department}</td>
        `;

        tableBody.appendChild(row);
    });
}

function searchStudents() {
    const search = document.getElementById("searchInput").value.trim();

    fetch(`/api/students?search=${encodeURIComponent(search)}`)
        .then(response => response.json())
        .then(students => {
            displayStudents(students);
        })
        .catch(error => {
            console.error("Search error:", error);
        });
}

document.addEventListener("DOMContentLoaded", loadStudents);
