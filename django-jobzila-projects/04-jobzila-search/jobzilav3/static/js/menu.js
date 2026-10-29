const menuButton = document.querySelector(".menu-toggle");
const navigationMenu = document.querySelector(".nav-menu");

if (menuButton && navigationMenu) {
    menuButton.addEventListener("click", function () {
        navigationMenu.classList.toggle("active");

        const isOpen = navigationMenu.classList.contains("active");

        menuButton.setAttribute("aria-expanded", isOpen);
        menuButton.textContent = isOpen ? "✕" : "☰";
    });
}