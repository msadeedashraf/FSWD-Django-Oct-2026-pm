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


const advancedSearchToggle = document.querySelector(
    "#advanced-search-toggle"
);

const advancedSearchBox = document.querySelector(
    "#advanced-search"
);

if (advancedSearchToggle && advancedSearchBox) {
    advancedSearchToggle.addEventListener("click", function () {
        advancedSearchBox.classList.toggle("show");

        const isOpen = advancedSearchBox.classList.contains("show");

        advancedSearchToggle.setAttribute(
            "aria-expanded",
            isOpen
        );

        advancedSearchToggle.textContent = isOpen
            ? "Hide Advanced Search"
            : "Advanced Search";
    });
}