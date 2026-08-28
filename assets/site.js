document.addEventListener("DOMContentLoaded", () => {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const nav = document.querySelector("#siteNav");
  const sticky = document.querySelector("#stickyCta");
  const hero = document.querySelector("#hero");

  const updateNav = () => nav.classList.toggle("is-condensed", scrollY > 36);
  updateNav();
  addEventListener("scroll", updateNav, { passive: true });

  new IntersectionObserver(([entry]) => {
    sticky.classList.toggle("visible", !entry.isIntersecting);
  }, { threshold: 0.05 }).observe(hero);

  if (reduced) {
    document.querySelectorAll(".reveal,.reveal-group").forEach((node) => node.classList.add("is-revealed"));
  } else {
    const reveal = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const target = entry.target.classList.contains("reveal-sentinel") ? entry.target.nextElementSibling : entry.target;
        if (target) target.classList.add("is-revealed");
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px" });
    document.querySelectorAll(".reveal,.reveal-sentinel").forEach((node) => reveal.observe(node));
  }

  if (window.GLightbox) GLightbox({ selector: ".glightbox", loop: true, touchNavigation: true, zoomable: true });

  const mapButton = document.querySelector("#loadMap");
  mapButton.addEventListener("click", () => {
    const shell = document.querySelector("#mapShell");
    const frame = document.createElement("iframe");
    frame.title = "Map of 4038 Northlight Drive, Naples, Florida";
    frame.loading = "lazy";
    frame.referrerPolicy = "no-referrer-when-downgrade";
    frame.src = "https://www.openstreetmap.org/export/embed.html?bbox=-81.79%2C26.10%2C-81.72%2C26.16&layer=mapnik&marker=26.127%2C-81.752";
    shell.replaceChildren(frame);
  }, { once: true });
});
