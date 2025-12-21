document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-link');

    navLinks.forEach(link => {
        if (link.pathname === currentPath) {
            link.classList.add('active-icon');
        } else {
            link.classList.remove('active-icon');
        }
    });

    // Código del botón Theme
    const btn = document.getElementById("theme");

    const defaultColors = {
    primary: getComputedStyle(document.documentElement).getPropertyValue("--color-primary").trim(),
    secondary: getComputedStyle(document.documentElement).getPropertyValue("--color-secondary").trim(),
    tertiary: getComputedStyle(document.documentElement).getPropertyValue("--color-tertiary").trim(),
    quaternary: getComputedStyle(document.documentElement).getPropertyValue("--color-quaternary").trim()
    };

    let toggled = false;

    btn.addEventListener("click", (e) => {
    e.preventDefault();
        if (!toggled) {
            document.documentElement.style.setProperty("--color-primary", "#FFFFFF");
            document.documentElement.style.setProperty("--color-secondary", "#AAAAAA");
            document.documentElement.style.setProperty("--color-tertiary", "#555555");
            document.documentElement.style.setProperty("--color-quaternary", "#000000");
        } else {
            document.documentElement.style.setProperty("--color-primary", defaultColors.primary);
            document.documentElement.style.setProperty("--color-secondary", defaultColors.secondary);
            document.documentElement.style.setProperty("--color-tertiary", defaultColors.tertiary);
            document.documentElement.style.setProperty("--color-quaternary", defaultColors.quaternary);
        }
        toggled = !toggled;
    });


});


