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

});


