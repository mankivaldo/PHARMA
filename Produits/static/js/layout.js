// Theme toggling
const themeToggle = document.querySelector(".theme-toggle");
const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

// Function to update theme
const updateTheme = (isDark) => {
  document.documentElement.classList.toggle("dark-mode", isDark);
  themeToggle.querySelector("i").classList.toggle("fa-sun", isDark);
  themeToggle.querySelector("i").classList.toggle("fa-moon", !isDark);
  localStorage.setItem("theme", isDark ? "dark" : "light");
};

// Check for saved theme preference or system preference
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
  updateTheme(savedTheme === "dark");
} else {
  updateTheme(prefersDarkScheme.matches);
}

// Listen for theme toggle clicks
themeToggle.addEventListener("click", () => {
  const isDark = !document.documentElement.classList.contains("dark-mode");
  updateTheme(isDark);
});

// Responsive sidebar
const menuToggle = document.getElementById("menu-toggle");
const sidebar = document.querySelector(".sidebar");
const appContainer = document.querySelector(".app-container");

menuToggle.addEventListener("click", () => {
  sidebar.classList.toggle("active");
  appContainer.classList.toggle("sidebar-active");
});

// Close sidebar when clicking outside on mobile
document.addEventListener("click", (e) => {
  if (window.innerWidth <= 768) {
    if (
      !sidebar.contains(e.target) &&
      !menuToggle.contains(e.target) &&
      sidebar.classList.contains("active")
    ) {
      sidebar.classList.remove("active");
      appContainer.classList.remove("sidebar-active");
    }
  }
});

// Handle window resize
window.addEventListener("resize", () => {
  if (window.innerWidth > 768) {
    sidebar.classList.remove("active");
    appContainer.classList.remove("sidebar-active");
  }
});

// Loading indicator functionality
const showLoading = () => document.body.classList.add("loading");
const hideLoading = () => document.body.classList.remove("loading");

// Add loading indicator for page transitions
document.addEventListener("click", (e) => {
  const link = e.target.closest("a");
  if (link && !link.target && !link.hasAttribute("download")) {
    showLoading();
  }
});

// Handle back/forward navigation
window.addEventListener("popstate", () => {
  showLoading();
});

// Hide loading indicator when page is fully loaded
window.addEventListener("load", hideLoading);

// Add loading indicator element to the DOM
const loadingIndicator = document.createElement("div");
loadingIndicator.className = "loading-indicator";
document.body.appendChild(loadingIndicator);
