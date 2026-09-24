// Confirm before deleting a student
document.querySelectorAll("form.confirm-delete").forEach(function (f) {
  f.addEventListener("submit", function (e) {
    if (!confirm("Delete this student? This cannot be undone.")) e.preventDefault();
  });
});
