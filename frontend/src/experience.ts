// Progressive enhancement: no content or controls depend on the motion bundles.
const motion = matchMedia("(prefers-reduced-motion: no-preference)");
const desktop = matchMedia("(min-width: 900px) and (pointer: fine)");
const connection = (
  navigator as Navigator & { connection?: { saveData?: boolean } }
).connection;
let generation = 0;
let cleanups: (() => void)[] = [];

async function enhance() {
  const current = ++generation;
  cleanups.forEach((clean) => clean());
  cleanups = [];
  // The editorial landing owns its motion; do not enhance its temporary fallback.
  if (document.querySelector("[data-agro-landing]") || !motion.matches || connection?.saveData) return;
  const { gsap } = await import("gsap");
  if (current !== generation) return;
  const context = gsap.context(() => {
    gsap.from(".hero-copy > *, .page-intro > *", {
      y: 16,
      duration: 0.65,
      stagger: 0.07,
      ease: "power2.out",
      clearProps: "all",
    });
  });
  cleanups.push(() => context.revert());
  // Observe once, never hide content while a bundle downloads.
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        gsap.fromTo(
          entry.target,
          { y: 16 },
          { y: 0, duration: 0.55, ease: "power2.out", clearProps: "transform" },
        );
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12 },
  );
  document
    .querySelectorAll(".feature-card, .how-section")
    .forEach((el) => observer.observe(el));
  cleanups.push(() => observer.disconnect());
  if (!desktop.matches) return;
  // Smooth wheel scrolling on the landing page only; forms, chat and touch retain native scrolling.
  if (document.querySelector(".farm-hero")) {
    const { default: LocomotiveScroll } = await import("locomotive-scroll");
    if (current !== generation) return;
    const scroll = new LocomotiveScroll({
      lenisOptions: {
        smoothWheel: true,
        lerp: 0.12,
        syncTouch: false,
        anchors: true,
        prevent: (node) =>
          !!node.closest("#chat-widget, .live-overlay, .navbar-collapse"),
      },
    });
    cleanups.push(() => scroll.destroy());
    const visibility = () => (document.hidden ? scroll.stop() : scroll.start());
    document.addEventListener("visibilitychange", visibility);
    cleanups.push(() =>
      document.removeEventListener("visibilitychange", visibility),
    );
  }
  const host = document.querySelector<HTMLElement>("#farm-scene");
  if (
    !host ||
    (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4)
  )
    return;
  try {
    const { createFarmScene } = await import("./farm-scene");
    if (current !== generation) return;
    cleanups.push(createFarmScene(host));
  } catch {
    /* The illustrated landscape remains visible when WebGL is unavailable. */
  }
}
void enhance().catch(() => {});
motion.addEventListener("change", () => {
  void enhance().catch(() => {});
});
desktop.addEventListener("change", () => {
  void enhance().catch(() => {});
});
window.addEventListener("pagehide", () => {
  generation++;
  cleanups.forEach((clean) => clean());
  cleanups = [];
});
window.addEventListener("pageshow", (event) => {
  if (event.persisted) void enhance().catch(() => {});
});

document
  .querySelectorAll<HTMLAnchorElement>(".navbar a.nav-link")
  .forEach((link) => {
    if (new URL(link.href).pathname === location.pathname && !link.hash)
      link.setAttribute("aria-current", "page");
  });
