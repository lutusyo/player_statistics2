
document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (sidebar && toggle) {
        toggle.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });
    }
});
