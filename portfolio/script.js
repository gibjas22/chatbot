// Navbar background on scroll.
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
});

// Mobile navigation toggle.
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
navToggle.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});

// Close the mobile menu once a link is chosen.
navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

// Highlight the active navigation link as sections scroll into view.
const sections = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');

const activeObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        navAnchors.forEach((a) => {
          a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
        });
      }
    });
  },
  { rootMargin: '-40% 0px -55% 0px' }
);

sections.forEach((section) => activeObserver.observe(section));

// Reveal cards as they enter the viewport.
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  },
  { threshold: 0.1 }
);

document
  .querySelectorAll('.about-card, .skill-category, .project-card, .timeline-item, .qual-group, .service-card')
  .forEach((el) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.55s ease, transform 0.55s ease';
    revealObserver.observe(el);
  });

// Contact form. This is a front-end demo handler.
// Wire the form to a backend or a service such as Formspree before going live.
const contactForm = document.getElementById('contactForm');
contactForm.addEventListener('submit', function (event) {
  event.preventDefault();
  const message = document.getElementById('formMessage');
  message.textContent = 'Thanks for reaching out. I will get back to you shortly.';
  message.className = 'form-message success';
  this.reset();
});
