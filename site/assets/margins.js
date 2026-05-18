(function () {
  var wideQuery = window.matchMedia("(min-width: 1080px)");
  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var state = null;
  var resizeTimer = 0;
  var animationFrame = 0;
  var paused = false;

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
      segments: [],
      segmentIndex: 0,
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
    state.segments = buildBranchingFractal(rect.width, rect.height);
    state.segmentIndex = 0;
    state.contentLeft = pageRect ? pageRect.left : rect.width / 2 - 380;
    state.contentRight = pageRect ? pageRect.right : rect.width / 2 + 380;
    state.context.clearRect(0, 0, width, height);
    state.context.lineCap = "round";
    state.context.lineJoin = "round";
    requestDraw();
  }

  function random(seed) {
    var value = Math.sin(seed * 12.9898) * 43758.5453;
    return value - Math.floor(value);
  }

  function angleBetween(start, end) {
    return Math.atan2(end.y - start.y, end.x - start.x);
  }

  function distanceBetween(start, end) {
    var dx = end.x - start.x;
    var dy = end.y - start.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function subdivideLine(start, end, depth, amplitude, seed) {
    if (depth === 0) {
      return [start, end];
    }

    var mid = {
      x: (start.x + end.x) / 2,
      y: (start.y + end.y) / 2
    };
    var angle = angleBetween(start, end) + Math.PI / 2;
    var offset = (random(seed + depth * 13) - 0.5) * amplitude;
    mid.x += Math.cos(angle) * offset;
    mid.y += Math.sin(angle) * offset;

    var left = subdivideLine(start, mid, depth - 1, amplitude * 0.55, seed + 7);
    var right = subdivideLine(mid, end, depth - 1, amplitude * 0.55, seed + 17);
    return left.slice(0, -1).concat(right);
  }

  function pushPolylineSegments(points, target, depth) {
    for (var i = 1; i < points.length; i += 1) {
      target.push({
        x1: points[i - 1].x,
        y1: points[i - 1].y,
        x2: points[i].x,
        y2: points[i].y,
        depth: depth
      });
    }
  }

  function growBranch(origin, angle, length, depth, seed, target) {
    if (depth <= 0 || length < 12) {
      return;
    }

    var end = {
      x: origin.x + Math.cos(angle) * length,
      y: origin.y + Math.sin(angle) * length
    };
    var points = subdivideLine(origin, end, 4, length * 0.38, seed);
    pushPolylineSegments(points, target, depth);

    var forkBase = points[Math.max(1, Math.floor(points.length * 0.62))];
    var secondFork = points[Math.max(1, Math.floor(points.length * 0.82))];
    var spread = 0.46 + random(seed + 31) * 0.32;
    growBranch(forkBase, angle - spread, length * 0.62, depth - 1, seed + 41, target);
    growBranch(forkBase, angle + spread, length * 0.56, depth - 1, seed + 53, target);
    growBranch(secondFork, angle + (random(seed + 67) - 0.5) * 1.1, length * 0.42, depth - 2, seed + 71, target);
  }

  function buildBranchingFractal(width, height) {
    var waypoints = [
      { x: -36, y: 84 },
      { x: width * 0.22, y: 64 },
      { x: width * 0.55, y: 114 },
      { x: width + 42, y: 82 },
      { x: width - 76, y: height * 0.34 },
      { x: width + 38, y: height * 0.56 },
      { x: width * 0.72, y: height * 0.78 },
      { x: width * 0.34, y: height * 0.62 },
      { x: -44, y: height * 0.82 },
      { x: width * 0.18, y: height + 40 }
    ];
    var segments = [];
    var branchSeed = 100;

    for (var i = 1; i < waypoints.length; i += 1) {
      var start = waypoints[i - 1];
      var end = waypoints[i];
      var length = distanceBetween(start, end);
      var trunkPoints = subdivideLine(start, end, 6, Math.min(118, length * 0.26), i * 23);
      for (var j = 1; j < trunkPoints.length; j += 1) {
        var previous = trunkPoints[j - 1];
        var current = trunkPoints[j];
        segments.push({
          x1: previous.x,
          y1: previous.y,
          x2: current.x,
          y2: current.y,
          depth: 5
        });

        if (j % 4 === 0) {
          var localAngle = angleBetween(previous, current);
          var side = (i + j) % 2 === 0 ? -1 : 1;
          var branchAngle = localAngle + side * (Math.PI / 2.45 + random(branchSeed) * 0.54);
          var branchLength = 42 + random(branchSeed + 3) * 126;
          growBranch(current, branchAngle, branchLength, 4, branchSeed, segments);
          branchSeed += 29;
        }
      }
    }

    return segments;
  }

  function segmentAlpha(midpointX, depth) {
    var fade = 110;
    var leftFade = Math.max(0, Math.min(1, (state.contentLeft - midpointX) / fade));
    var rightFade = Math.max(0, Math.min(1, (midpointX - state.contentRight) / fade));
    var marginStrength = Math.max(leftFade, rightFade);
    var depthBoost = depth >= 5 ? 0.03 : 0;
    return 0.035 + depthBoost + marginStrength * 0.17;
  }

  function strokeSegment(segment) {
    var context = state.context;
    var scale = state.scale;
    var midpointX = (segment.x1 + segment.x2) / 2;
    var depth = segment.depth || 1;

    context.beginPath();
    context.moveTo(segment.x1 * scale, segment.y1 * scale);
    context.lineTo(segment.x2 * scale, segment.y2 * scale);
    context.lineWidth = Math.max(0.55, depth * 0.24) * scale;
    context.strokeStyle = "rgba(139, 30, 63, " + segmentAlpha(midpointX, depth).toFixed(3) + ")";
    context.stroke();
  }

  function draw() {
    animationFrame = 0;
    if (!shouldRun() || paused || !state) {
      return;
    }

    if (state.segmentIndex >= state.segments.length) {
      return;
    }

    var segmentsThisFrame = 16;
    for (var i = 0; i < segmentsThisFrame && state.segmentIndex < state.segments.length; i += 1) {
      strokeSegment(state.segments[state.segmentIndex]);
      state.segmentIndex += 1;
    }

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
