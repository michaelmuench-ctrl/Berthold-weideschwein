(function () {
  var topWrap = document.getElementById("top-wrap");
  var nav = document.getElementById("main-nav");
  var toggle = document.getElementById("nav-toggle");

  function onScroll() {
    if (window.scrollY > 40) {
      topWrap.classList.add("is-scrolled");
    } else {
      topWrap.classList.remove("is-scrolled");
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  function setNav(open) {
    nav.classList.toggle("open", open);
    document.body.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
  }
  toggle.addEventListener("click", function () {
    setNav(toggle.getAttribute("aria-expanded") !== "true");
  });
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) setNav(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setNav(false);
  });

  var form = document.getElementById("newsletter-form");
  var note = document.getElementById("newsletter-note");
  var email = document.getElementById("newsletter-email");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var value = email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        note.textContent = "Bitte geben Sie eine gültige E-Mail-Adresse ein.";
        note.classList.remove("is-success");
        email.focus();
        return;
      }
      note.textContent = "Danke! Bitte bestätigen Sie die E-Mail, die wir Ihnen gerade geschickt haben.";
      note.classList.add("is-success");
      form.reset();
    });
  }

  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
