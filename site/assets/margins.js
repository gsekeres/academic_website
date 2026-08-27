(function () {
  // A latent-space network sampled from Gaussian mixtures on either side of
  // the content, with local geometric links and a few cross-cloud bridges.
  var REVEAL_SECONDS = 2.25;
  var SESSION_SEED_KEY = "gabe-margin-network-seed";
  var SESSION_REVEALED_KEY = "gabe-gaussian-network-revealed-v1";

  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var pane = null;
  var canvas = null;
  var context = null;
  var model = null;
  var animationFrame = 0;
  var animationStart = 0;
  var lastDraw = 0;
  var resizeTimer = 0;
  var elapsedBeforePause = 0;
  var forceStatic = false;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function readSession(key) {
    try {
      return window.sessionStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function writeSession(key, value) {
    try {
      window.sessionStorage.setItem(key, String(value));
    } catch (error) {
      // The network still works when session storage is unavailable.
    }
  }

  function makeSeed() {
    if (window.crypto && window.crypto.getRandomValues) {
      var values = new Uint32Array(1);
      window.crypto.getRandomValues(values);
      return values[0] >>> 0;
    }
    return (Date.now() ^ Math.floor(Math.random() * 0xffffffff)) >>> 0;
  }

  function getSeed() {
    var stored = Number(readSession(SESSION_SEED_KEY));
    if (Number.isFinite(stored) && stored > 0) {
      return stored >>> 0;
    }
    var seed = makeSeed();
    writeSession(SESSION_SEED_KEY, seed);
    return seed;
  }

  function mulberry32(seed) {
    return function () {
      var value = (seed += 0x6d2b79f5);
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }

  function makeNormalRandom(random) {
    var spare = null;
    return function () {
      if (spare !== null) {
        var value = spare;
        spare = null;
        return value;
      }

      var u = 0;
      var v = 0;
      while (u === 0) {
        u = random();
      }
      while (v === 0) {
        v = random();
      }
      var magnitude = Math.sqrt(-2 * Math.log(u));
      var angle = Math.PI * 2 * v;
      spare = magnitude * Math.sin(angle);
      return magnitude * Math.cos(angle);
    };
  }

  function connectionSavesData() {
    var connection =
      navigator.connection ||
      navigator.mozConnection ||
      navigator.webkitConnection;
    return Boolean(connection && connection.saveData);
  }

  function createCanvas() {
    pane = document.createElement("div");
    canvas = document.createElement("canvas");
    pane.className = "margin-network";
    pane.setAttribute("aria-hidden", "true");
    canvas.setAttribute("aria-hidden", "true");
    pane.appendChild(canvas);
    document.body.appendChild(pane);
    context = canvas.getContext("2d", { alpha: true });
    if (!context) {
      pane.remove();
      pane = null;
      canvas = null;
    }
  }

  function removeCanvas() {
    if (animationFrame) {
      window.cancelAnimationFrame(animationFrame);
      animationFrame = 0;
    }
    if (pane) {
      pane.remove();
    }
    pane = null;
    canvas = null;
    context = null;
    model = null;
  }

  function contentBounds(viewportWidth) {
    var elements = [
      document.querySelector(".page"),
      document.querySelector(".nav"),
      document.querySelector(".footer")
    ].filter(Boolean);
    var rects = elements.map(function (element) {
      return element.getBoundingClientRect();
    });

    if (!rects.length) {
      return { left: viewportWidth * 0.2, right: viewportWidth * 0.8 };
    }

    return {
      left: clamp(
        Math.min.apply(
          Math,
          rects.map(function (rect) {
            return rect.left;
          })
        ),
        0,
        viewportWidth
      ),
      right: clamp(
        Math.max.apply(
          Math,
          rects.map(function (rect) {
            return rect.right;
          })
        ),
        0,
        viewportWidth
      )
    };
  }

  function pickComponent(random) {
    var value = random();
    if (value < 0.28) {
      return 0;
    }
    if (value < 0.72) {
      return 1;
    }
    return 2;
  }

  function makeNode(
    side,
    index,
    component,
    centerX,
    sigmaX,
    maxX,
    minX,
    viewportHeight,
    random,
    normal
  ) {
    var yCenters = [0.16, 0.5, 0.84];
    var ySigmas = [0.13, 0.19, 0.13];
    var x = centerX;
    var y = viewportHeight * yCenters[component];

    for (var attempt = 0; attempt < 12; attempt += 1) {
      var candidateX = centerX + normal() * sigmaX;
      var candidateY =
        viewportHeight * yCenters[component] +
        normal() * viewportHeight * ySigmas[component];
      if (
        candidateX >= minX &&
        candidateX <= maxX &&
        candidateY >= -16 &&
        candidateY <= viewportHeight + 16
      ) {
        x = candidateX;
        y = candidateY;
        break;
      }
    }

    return {
      index: index,
      side: side,
      component: component,
      x: clamp(x, minX, Math.max(minX, maxX)),
      y: clamp(y, -8, viewportHeight + 8),
      radius: 0.85 + random() * 0.58,
      birth: 0.08 + random() * 0.84,
      bridge: false
    };
  }

  function edgeKey(a, b) {
    return a < b ? a + ":" + b : b + ":" + a;
  }

  function distanceSquared(a, b) {
    var dx = b.x - a.x;
    var dy = b.y - a.y;
    return dx * dx + dy * dy;
  }

  function makeLocalEdges(nodes, random, viewportWidth, viewportHeight) {
    var edges = [];
    var seen = new Set();
    var localRadius = clamp(
      Math.sqrt(viewportWidth * viewportHeight) / 5,
      96,
      180
    );
    var radiusSquared = localRadius * localRadius;

    nodes.forEach(function (source) {
      var candidates = nodes
        .filter(function (target) {
          return target.side === source.side && target.index !== source.index;
        })
        .map(function (target) {
          return { target: target, distance: distanceSquared(source, target) };
        })
        .sort(function (a, b) {
          return a.distance - b.distance;
        });

      var neighborCount = random() < 0.22 ? 3 : 2;
      candidates.slice(0, neighborCount).forEach(function (candidate, rank) {
        if (candidate.distance > radiusSquared && rank > 0) {
          return;
        }
        var key = edgeKey(source.index, candidate.target.index);
        if (seen.has(key)) {
          return;
        }
        seen.add(key);
        edges.push({
          a: source.index,
          b: candidate.target.index,
          start: Math.max(source.birth, candidate.target.birth),
          duration: 0.24
        });
      });
    });

    return edges;
  }

  function bridgeCurve(a, b, random, viewportWidth, viewportHeight) {
    var dx = b.x - a.x;
    var dy = b.y - a.y;
    var distance = Math.max(1, Math.sqrt(dx * dx + dy * dy));
    var normalX = -dy / distance;
    var normalY = dx / distance;
    var direction = random() < 0.5 ? -1 : 1;
    var bow = Math.min(72, Math.max(18, distance * 0.09));

    return {
      cx: clamp(
        (a.x + b.x) / 2 + normalX * bow * direction,
        8,
        viewportWidth - 8
      ),
      cy: clamp(
        (a.y + b.y) / 2 + normalY * bow * direction,
        -24,
        viewportHeight + 24
      )
    };
  }

  function makeBridges(nodes, random, viewportWidth, viewportHeight) {
    var left = nodes.filter(function (node) {
      return node.side === "left";
    });
    var right = nodes.filter(function (node) {
      return node.side === "right";
    });
    var bridgeCount = viewportWidth < 760 ? 2 : 3;
    var bridges = [];
    var seen = new Set();

    for (var index = 0; index < bridgeCount; index += 1) {
      var source = left[Math.floor(random() * left.length)];
      var candidates = right
        .map(function (target) {
          return {
            target: target,
            score:
              Math.abs(source.y - target.y) * (0.75 + random() * 0.5) +
              random() * viewportHeight * 0.08
          };
        })
        .sort(function (a, b) {
          return a.score - b.score;
        });
      var target = candidates[Math.floor(random() * Math.min(4, candidates.length))].target;
      var key = edgeKey(source.index, target.index);
      if (seen.has(key)) {
        index -= 1;
        continue;
      }
      seen.add(key);
      source.bridge = true;
      target.bridge = true;
      var control = bridgeCurve(
        source,
        target,
        random,
        viewportWidth,
        viewportHeight
      );
      bridges.push({
        a: source.index,
        b: target.index,
        cx: control.cx,
        cy: control.cy,
        start: 1.1 + index * 0.12,
        duration: 0.5
      });
    }

    return bridges;
  }

  function buildNetwork(viewportWidth, viewportHeight, seed) {
    var random = mulberry32(seed >>> 0);
    var normal = makeNormalRandom(random);
    var bounds = contentBounds(viewportWidth);
    var leftMargin = Math.max(0, bounds.left);
    var rightMargin = Math.max(0, viewportWidth - bounds.right);
    var leftCenter = clamp(
      leftMargin * 0.52,
      viewportWidth * 0.1,
      viewportWidth * 0.24
    );
    var rightCenter = clamp(
      bounds.right + rightMargin * 0.48,
      viewportWidth * 0.76,
      viewportWidth * 0.9
    );
    var leftSigma = clamp(
      Math.max(viewportWidth * 0.05, leftMargin * 0.38),
      34,
      140
    );
    var rightSigma = clamp(
      Math.max(viewportWidth * 0.05, rightMargin * 0.38),
      34,
      140
    );
    var contentTail = Math.max(42, viewportWidth * 0.08);
    var leftMax = Math.min(viewportWidth * 0.48, bounds.left + contentTail);
    var rightMin = Math.max(viewportWidth * 0.52, bounds.right - contentTail);
    var nodeCount = clamp(
      Math.round((viewportWidth * viewportHeight) / 4500),
      176,
      360
    );
    var leftCount = Math.ceil(nodeCount / 2);
    var nodes = [];

    for (var leftIndex = 0; leftIndex < leftCount; leftIndex += 1) {
      nodes.push(
        makeNode(
          "left",
          nodes.length,
          pickComponent(random),
          leftCenter,
          leftSigma,
          Math.max(6, leftMax),
          4,
          viewportHeight,
          random,
          normal
        )
      );
    }

    for (var rightIndex = leftCount; rightIndex < nodeCount; rightIndex += 1) {
      nodes.push(
        makeNode(
          "right",
          nodes.length,
          pickComponent(random),
          rightCenter,
          rightSigma,
          viewportWidth - 4,
          Math.min(viewportWidth - 6, rightMin),
          viewportHeight,
          random,
          normal
        )
      );
    }

    return {
      nodes: nodes,
      localEdges: makeLocalEdges(nodes, random, viewportWidth, viewportHeight),
      bridges: makeBridges(nodes, random, viewportWidth, viewportHeight)
    };
  }

  function quadraticPoint(a, edge, b, time) {
    var inverse = 1 - time;
    return {
      x:
        inverse * inverse * a.x +
        2 * inverse * time * edge.cx +
        time * time * b.x,
      y:
        inverse * inverse * a.y +
        2 * inverse * time * edge.cy +
        time * time * b.y
    };
  }

  function edgeProgress(elapsed, edge) {
    return clamp((elapsed - edge.start) / edge.duration, 0, 1);
  }

  function drawNetwork(elapsed) {
    var nodes = model.network.nodes;
    context.lineCap = "round";
    context.lineJoin = "round";

    context.beginPath();
    model.network.localEdges.forEach(function (edge) {
      var progress = edgeProgress(elapsed, edge);
      if (progress <= 0) {
        return;
      }
      var a = nodes[edge.a];
      var b = nodes[edge.b];
      context.moveTo(a.x, a.y);
      context.lineTo(
        a.x + (b.x - a.x) * progress,
        a.y + (b.y - a.y) * progress
      );
    });
    context.strokeStyle = "rgba(29, 29, 31, 0.052)";
    context.lineWidth = 0.72;
    context.stroke();

    context.beginPath();
    model.network.bridges.forEach(function (edge) {
      var progress = edgeProgress(elapsed, edge);
      if (progress <= 0) {
        return;
      }
      var a = nodes[edge.a];
      var b = nodes[edge.b];
      var steps = Math.max(1, Math.ceil(progress * 14));
      context.moveTo(a.x, a.y);
      for (var step = 1; step <= steps; step += 1) {
        var time = Math.min(progress, step / 14);
        var point = quadraticPoint(a, edge, b, time);
        context.lineTo(point.x, point.y);
      }
    });
    context.strokeStyle = "rgba(139, 30, 63, 0.09)";
    context.lineWidth = 0.9;
    context.stroke();

    nodes.forEach(function (node) {
      var progress = clamp((elapsed - node.birth) / 0.18, 0, 1);
      if (progress <= 0) {
        return;
      }
      context.globalAlpha = progress;
      context.beginPath();
      context.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      context.fillStyle = "rgba(29, 29, 31, 0.19)";
      context.fill();

      if (node.bridge && elapsed > 1.08) {
        context.beginPath();
        context.arc(node.x, node.y, Math.max(0.58, node.radius * 0.54), 0, Math.PI * 2);
        context.fillStyle = "rgba(139, 30, 63, 0.34)";
        context.fill();
      }
    });
    context.globalAlpha = 1;
  }

  function draw(elapsed) {
    if (!context || !model) {
      return;
    }
    context.clearRect(0, 0, model.width, model.height);
    drawNetwork(elapsed);
  }

  function finishReveal() {
    animationFrame = 0;
    elapsedBeforePause = REVEAL_SECONDS;
    draw(REVEAL_SECONDS);
    writeSession(SESSION_REVEALED_KEY, "1");
  }

  function animate(timestamp) {
    animationFrame = 0;
    if (document.hidden || !model) {
      return;
    }
    if (!animationStart) {
      animationStart = timestamp - elapsedBeforePause * 1000;
    }
    var elapsed = (timestamp - animationStart) / 1000;
    elapsedBeforePause = elapsed;

    if (timestamp - lastDraw >= 32) {
      draw(elapsed);
      lastDraw = timestamp;
    }
    if (elapsed >= REVEAL_SECONDS) {
      finishReveal();
      return;
    }
    animationFrame = window.requestAnimationFrame(animate);
  }

  function startReveal() {
    var alreadyRevealed = readSession(SESSION_REVEALED_KEY) === "1";
    var staticMode =
      forceStatic || reduceQuery.matches || connectionSavesData() || alreadyRevealed;
    animationStart = 0;
    lastDraw = 0;
    elapsedBeforePause = 0;

    if (staticMode) {
      draw(REVEAL_SECONDS);
      return;
    }
    animationFrame = window.requestAnimationFrame(animate);
  }

  function rebuild() {
    if (animationFrame) {
      window.cancelAnimationFrame(animationFrame);
      animationFrame = 0;
    }

    if (!document.querySelector(".page")) {
      removeCanvas();
      return;
    }
    if (!pane) {
      createCanvas();
    }
    if (!context) {
      return;
    }

    var width = Math.max(1, window.innerWidth);
    var height = Math.max(1, window.innerHeight);
    var scale = Math.min(1.5, window.devicePixelRatio || 1);
    var baseSeed = getSeed();

    canvas.width = Math.floor(width * scale);
    canvas.height = Math.floor(height * scale);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    context.setTransform(scale, 0, 0, scale, 0, 0);
    model = {
      width: width,
      height: height,
      network: buildNetwork(width, height, baseSeed ^ 0x9e3779b9)
    };
    startReveal();
  }

  function handleResize() {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(function () {
      forceStatic = true;
      rebuild();
    }, 180);
  }

  function handleVisibility() {
    if (document.hidden) {
      if (animationFrame) {
        window.cancelAnimationFrame(animationFrame);
        animationFrame = 0;
      }
      return;
    }
    if (model && elapsedBeforePause < REVEAL_SECONDS && !animationFrame) {
      animationStart = performance.now() - elapsedBeforePause * 1000;
      animationFrame = window.requestAnimationFrame(animate);
    }
  }

  function listenToQuery(query) {
    var onChange = function () {
      forceStatic = true;
      rebuild();
    };
    if (query.addEventListener) {
      query.addEventListener("change", onChange);
    } else {
      query.addListener(onChange);
    }
  }

  listenToQuery(reduceQuery);
  window.addEventListener("resize", handleResize, { passive: true });
  document.addEventListener("visibilitychange", handleVisibility);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", rebuild, { once: true });
  } else {
    rebuild();
  }
})();
