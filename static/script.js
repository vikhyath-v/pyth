const header = document.querySelector('header');
const navLinks = document.querySelectorAll('.nav-links li a');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
        navLinks.forEach(link => {
            link.style.color = '#eae2d8';
        });
    } else {
        header.style.backgroundColor = 'transparent';
        navLinks.forEach(link => {
            link.style.color = '#955200';
        });
    }
});

// Logo hover effect
const logo = document.querySelector('#limg');
logo.addEventListener('mouseover', () => {
    logo.style.transform = 'scale(1.1)';
});
logo.addEventListener('mouseout', () => {
    logo.style.transform = 'scale(1)';
});