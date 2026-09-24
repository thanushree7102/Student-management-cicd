document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registrationForm");
    const message = document.getElementById("message");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = {
            name: document.getElementById("name").value.trim(),
            usn: document.getElementById("usn").value.trim(),
            date_of_birth: document.getElementById("date_of_birth").value,
            gender: document.getElementById("gender").value,
            department: document.getElementById("department").value,
            semester: document.getElementById("semester").value,
            section: document.getElementById("section").value.trim(),
            admission_year: document.getElementById("admission_year").value,
            email: document.getElementById("email").value.trim(),
            phone: document.getElementById("phone").value.trim(),
            address: document.getElementById("address").value.trim(),
            parent_name: document.getElementById("parent_name").value.trim(),
            parent_phone: document.getElementById("parent_phone").value.trim()
        };

        if (!formData.name || !formData.usn || !formData.email) {
            message.textContent = "Please fill in all required fields.";
            return;
        }

        try {
            const response = await fetch("/registration/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            message.textContent = result.message;

            if (result.success) {
                form.reset();
            }
        } catch (error) {
            console.error("Registration error:", error);
            message.textContent = "Unable to connect to the server.";
        }
    });
});