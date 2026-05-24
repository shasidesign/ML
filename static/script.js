/* Prediction form loader */
const form = document.getElementById("prediction-form");
if (form) {
    form.addEventListener("submit", function () {
        const loader = document.getElementById("loader");
        if (loader) loader.style.display = "flex";
    });
}

/* Dark / Light theme toggle — safe null check */
const themeToggle = document.getElementById("theme-toggle");
if (themeToggle) {
    const saved = localStorage.getItem("theme");
    if (saved === "light") {
        document.body.classList.add("light-mode");
        themeToggle.textContent = "☀️";
    }
    themeToggle.addEventListener("click", function () {
        const isLight = document.body.classList.toggle("light-mode");
        themeToggle.textContent = isLight ? "☀️" : "🌙";
        localStorage.setItem("theme", isLight ? "light" : "dark");
    });
}