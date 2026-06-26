(function () {
  var wideQuery = window.matchMedia("(min-width: 1080px)");
  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var state = null;
  var resizeTimer = 0;
  var animationFrame = 0;
  var paused = false;

  var FERN_COLOR = "34, 130, 56"; // green
  var BG_COLOR = "251, 251, 250"; // matches --bg; used to gently fade older points
  var FADE_ALPHA = 0.014; // per-frame fade so the fern keeps actively redrawing
  var POINTS_PER_FRAME = 1800; // chaos-game points plotted each frame
  var FERN_SIZE = 1.2; // >1 overshoots the aim point, enlarging the fern
  var FERN_AIM_Y = 0.5; // tip aims at this fraction down the right edge

  function shouldRun() {
    return wideQuery.matches && !reduceQuery.matches;
  }

  function createState() {
    var pane = document.createElement("div");
    var canvas = document.createElement("canvas");
    pane.className = "margin-fractal";
    pane.setAttribute("aria-hidden", "true");
    canvas.setAttribute("aria-hidden", "true");
    pane.appendChild(canvas);
    document.body.appendChild(pane);
    return {
      pane: pane,
      canvas: canvas,
      context: canvas.getContext("2d", { alpha: true }),
      width: 0,
      height: 0,
      scale: 1,
      fx: 0,
      fy: 0,
      settle: 0,
      alongX: 1,
      alongY: 0,
      perpX: 0,
      perpY: 1,
      unit: 1,
      contentLeft: 0,
      contentRight: 0
    };
  }

  function removeState() {
    if (state) {
      state.pane.remove();
      state = null;
    }
    if (animationFrame) {
      window.cancelAnimationFrame(animationFrame);
      animationFrame = 0;
    }
  }

  function resetAll() {
    if (!shouldRun()) {
      removeState();
      return;
    }

    if (!state) {
      state = createState();
    }

    var rect = state.pane.getBoundingClientRect();
    var scale = Math.min(1.5, window.devicePixelRatio || 1);
    var width = Math.max(1, Math.floor(rect.width * scale));
    var height = Math.max(1, Math.floor(rect.height * scale));
    var page = document.querySelector(".page");
    var pageRect = page ? page.getBoundingClientRect() : null;

    state.canvas.width = width;
    state.canvas.height = height;
    state.width = width;
    state.height = height;
    state.scale = scale;

    // Lay the fern from the top-left corner toward the middle of the right edge.
    var aimY = rect.height * FERN_AIM_Y;
    var theta = Math.atan2(aimY, rect.width);
    state.alongX = Math.cos(theta);
    state.alongY = Math.sin(theta);
    state.perpX = -Math.sin(theta);
    state.perpY = Math.cos(theta);
    var aimDist = Math.sqrt(rect.width * rect.width + aimY * aimY);
    state.unit = (aimDist * FERN_SIZE) / 10; // fern is ~10 tall in its own coordinates

    state.fx = 0;
    state.fy = 0;
    state.settle = 0;
    state.contentLeft = pageRect ? pageRect.left : rect.width / 2 - 380;
    state.contentRight = pageRect ? pageRect.right : rect.width / 2 + 380;
    state.context.clearRect(0, 0, width, height);
    requestDraw();
  }

  function pointAlpha(pointX) {
    var fade = 120;
    var leftFade = Math.max(0, Math.min(1, (state.contentLeft - pointX) / fade));
    var rightFade = Math.max(0, Math.min(1, (pointX - state.contentRight) / fade));
    var marginStrength = Math.max(leftFade, rightFade);
    return 0.05 + marginStrength * 0.18;
  }

  // One animation frame of the Barnsley fern chaos game. The orbit is kept live
  // across frames and points are plotted continuously, while a faint fade erases
  // the oldest points so the fern is perpetually being drawn rather than static.
  function stepFern() {
    var context = state.context;
    var scale = state.scale;
    var size = Math.max(1, scale);

    context.fillStyle = "rgba(" + BG_COLOR + ", " + FADE_ALPHA + ")";
    context.fillRect(0, 0, state.width, state.height);

    var x = state.fx;
    var y = state.fy;
    for (var i = 0; i < POINTS_PER_FRAME; i += 1) {
      var r = Math.random();
      var nx, ny;
      if (r < 0.01) {
        nx = 0;
        ny = 0.16 * y;
      } else if (r < 0.86) {
        nx = 0.85 * x + 0.04 * y;
        ny = -0.04 * x + 0.85 * y + 1.6;
      } else if (r < 0.93) {
        nx = 0.20 * x - 0.26 * y;
        ny = 0.23 * x + 0.22 * y + 1.6;
      } else {
        nx = -0.15 * x + 0.28 * y;
        ny = 0.26 * x + 0.24 * y + 0.44;
      }
      x = nx;
      y = ny;

      if (state.settle < 20) {
        state.settle += 1; // let the orbit settle onto the attractor
        continue;
      }

      var along = y * state.unit;
      var perp = x * state.unit;
      var cx = state.alongX * along + state.perpX * perp;
      var cy = state.alongY * along + state.perpY * perp;
      context.fillStyle = "rgba(" + FERN_COLOR + ", " + pointAlpha(cx).toFixed(3) + ")";
      context.fillRect(cx * scale, cy * scale, size, size);
    }

    state.fx = x;
    state.fy = y;
  }

  function draw() {
    animationFrame = 0;
    if (!shouldRun() || paused || !state) {
      return;
    }

    stepFern();
    animationFrame = window.requestAnimationFrame(draw);
  }

  function requestDraw() {
    if (!animationFrame && shouldRun() && !paused) {
      animationFrame = window.requestAnimationFrame(draw);
    }
  }

  function handleResize() {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(resetAll, 180);
  }

  function handleVisibility() {
    paused = document.hidden;
    if (!paused) {
      requestDraw();
    }
  }

  function listenToQuery(query) {
    if (query.addEventListener) {
      query.addEventListener("change", resetAll);
    } else {
      query.addListener(resetAll);
    }
  }

  listenToQuery(wideQuery);
  listenToQuery(reduceQuery);
  window.addEventListener("resize", handleResize, { passive: true });
  document.addEventListener("visibilitychange", handleVisibility);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", resetAll, { once: true });
  } else {
    resetAll();
  }
})();
