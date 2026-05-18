(function () {
  function shouldOpenInNewTab(link) {
    var href = link.getAttribute("href");
    var url;

    if (!href || href.indexOf("mailto:") === 0 || href.indexOf("tel:") === 0) {
      return false;
    }

    try {
      url = new URL(href, window.location.href);
    } catch (error) {
      return false;
    }

    return (
      url.origin !== window.location.origin ||
      url.pathname === "/assets/cv/gabe_sekeres_cv.pdf"
    );
  }

  function openLinksInNewTabs() {
    document.querySelectorAll("a[href]").forEach(function (link) {
      if (shouldOpenInNewTab(link)) {
        link.setAttribute("target", "_blank");
        link.setAttribute("rel", "noopener noreferrer");
      } else {
        link.removeAttribute("target");
        link.removeAttribute("rel");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", openLinksInNewTabs, { once: true });
  } else {
    openLinksInNewTabs();
  }
})();
