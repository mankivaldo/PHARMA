document.addEventListener("DOMContentLoaded", function () {
  // Fonctionnalité pour réduire/agrandir le sidebar
  const logoIcon = document.querySelector(".logo-details i");
  if (logoIcon) {
    logoIcon.addEventListener("click", () => {
      document.querySelector(".sidebar").classList.toggle("close");
    });
  }

  // Pour le mode responsive - détecte le clic sur l'icône du menu
  const menuIcon = document.querySelector(".menu-icon");
  if (menuIcon) {
    menuIcon.addEventListener("click", () => {
      document.querySelector(".sidebar").classList.toggle("open");
    });
  }
});
