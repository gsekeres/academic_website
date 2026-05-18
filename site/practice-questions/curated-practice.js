(function () {
  var state = {
    questions: [],
    activeQuestion: null,
    communityRequestToken: 0
  };

  function getElement(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderText(value) {
    return escapeHtml(value)
      .split(/\n{2,}/)
      .map(function (paragraph) {
        return "<p>" + paragraph.replace(/\n/g, "<br>") + "</p>";
      })
      .join("");
  }

  function titleCase(value) {
    var normalized = String(value || "").replace(/_/g, " ").trim();
    var special = {
      math: "Math",
      micro: "Micro",
      "game theory": "Game Theory"
    };
    if (special[normalized]) {
      return special[normalized];
    }
    return normalized.replace(/\b[a-z]/g, function (match) {
      return match.toUpperCase();
    });
  }

  function renderTags(question) {
    var tags = [
      question.main_domain,
      question.subdomain,
      question.difficulty,
      question.variant_type,
      question.source_family
    ].concat(question.tags || []);

    return tags
      .filter(Boolean)
      .filter(function (tag, index, array) {
        return array.indexOf(tag) === index;
      })
      .map(function (tag) {
        return "<span>" + escapeHtml(titleCase(tag)) + "</span>";
      })
      .join("");
  }

  function pickQuestion() {
    if (!state.questions.length) {
      return null;
    }
    var index = Math.floor(Math.random() * state.questions.length);
    return state.questions[index];
  }

  function typesetMath() {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([
        getElement("question-prompt"),
        getElement("question-title"),
        getElement("answer-preview"),
        getElement("community-solutions-list"),
        getElement("question-hint"),
        getElement("question-solution")
      ]);
    }
  }

  function renderMarkdown(value) {
    var escaped = escapeHtml(value || "");
    var placeholders = [];

    escaped = escaped.replace(/```([\s\S]*?)```/g, function (_, code) {
      var token = "\u0000CODE" + placeholders.length + "\u0000";
      placeholders.push("<pre><code>" + code.trim() + "</code></pre>");
      return token;
    });

    escaped = escaped.replace(/`([^`]+)`/g, "<code>$1</code>");
    escaped = escaped.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    escaped = escaped.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
    escaped = escaped.replace(/^#### (.+)$/gm, "<h4>$1</h4>");
    escaped = escaped.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    escaped = escaped.replace(/^## (.+)$/gm, "<h3>$1</h3>");
    escaped = escaped.replace(/^# (.+)$/gm, "<h3>$1</h3>");

    escaped = escaped.replace(/(?:^|\n)((?:[-*] .+(?:\n|$))+)/g, function (_, block) {
      var items = block.trim().split(/\n/).map(function (line) {
        return "<li>" + line.replace(/^[-*] /, "") + "</li>";
      }).join("");
      return "\n<ul>" + items + "</ul>\n";
    });

    escaped = escaped.replace(/(?:^|\n)((?:\d+\. .+(?:\n|$))+)/g, function (_, block) {
      var items = block.trim().split(/\n/).map(function (line) {
        return "<li>" + line.replace(/^\d+\. /, "") + "</li>";
      }).join("");
      return "\n<ol>" + items + "</ol>\n";
    });

    placeholders.forEach(function (html, index) {
      escaped = escaped.replace("\u0000CODE" + index + "\u0000", html);
    });

    return escaped
      .split(/\n{2,}/)
      .map(function (block) {
        var trimmed = block.trim();
        if (!trimmed) {
          return "";
        }
        if (/^<(h3|h4|ul|ol|pre)\b/.test(trimmed)) {
          return trimmed;
        }
        return "<p>" + trimmed.replace(/\n/g, "<br>") + "</p>";
      })
      .join("");
  }

  function renderQuestion(question) {
    state.activeQuestion = question;
    getElement("question-title").innerHTML = escapeHtml(question.title);
    getElement("question-meta").innerHTML = renderTags(question);
    getElement("question-prompt").innerHTML =
      renderText(question.preliminaries) + renderText(question.question);
    getElement("question-hint").hidden = true;
    getElement("question-solution").hidden = true;
    getElement("answer-preview").hidden = true;
    getElement("answer-preview").innerHTML = "";
    getElement("solution-submit-status").textContent = "";
    getElement("question-hint").innerHTML = renderText(question.learning_objective);
    getElement("question-solution").innerHTML = renderText(question.solution);
    getElement("answer-draft").value = "";
    updateIssueReportQuestion(question);
    loadCommunitySolutions(question);
    typesetMath();
  }

  function updateIssueReportQuestion(question) {
    var idField = getElement("issue-question-id");
    var titleField = getElement("issue-question-title");
    var urlField = getElement("issue-page-url");
    var currentQuestion = getElement("issue-current-question");
    if (!idField || !titleField || !urlField || !currentQuestion) {
      return;
    }

    idField.value = question.id || "";
    titleField.value = question.title || "";
    urlField.value = window.location.href.split("#")[0];
    currentQuestion.textContent = question.id
      ? "Reporting on current question: " + question.id
      : "Current question will be attached automatically.";
  }

  function showRandomQuestion() {
    var question = pickQuestion();
    if (question) {
      renderQuestion(question);
    }
  }

  function togglePanel(id) {
    var panel = getElement(id);
    panel.hidden = !panel.hidden;
    typesetMath();
  }

  function renderAnswerDraft() {
    var draft = getElement("answer-draft").value.trim();
    var preview = getElement("answer-preview");
    preview.hidden = false;
    preview.innerHTML = draft ? renderMarkdown(draft) : "<p>Write a solution draft first.</p>";
    typesetMath();
  }

  function communityEndpoint(questionId) {
    return "/.netlify/functions/community-solutions?questionId=" + encodeURIComponent(questionId);
  }

  function statusMessage(message) {
    getElement("solution-submit-status").textContent = message;
  }

  function votedKey(questionId, solutionId) {
    return "practice-vote:" + questionId + ":" + solutionId;
  }

  function hasVoted(questionId, solutionId) {
    try {
      return window.localStorage.getItem(votedKey(questionId, solutionId)) === "1";
    } catch (_) {
      return false;
    }
  }

  function markVoted(questionId, solutionId) {
    try {
      window.localStorage.setItem(votedKey(questionId, solutionId), "1");
    } catch (_) {
      return;
    }
  }

  function renderCommunitySolutions(solutions) {
    var list = getElement("community-solutions-list");
    var question = state.activeQuestion;
    if (!question) {
      return;
    }
    if (!solutions.length) {
      list.innerHTML = "<p class=\"muted-note\">No proposed solutions yet.</p>";
      return;
    }

    list.innerHTML = solutions.map(function (solution) {
      var alreadyVoted = hasVoted(question.id, solution.id);
      return [
        "<article class=\"community-solution\">",
        "<div class=\"community-solution-meta\">",
        "<span>" + escapeHtml(solution.author || "Anonymous") + "</span>",
        "<span>" + escapeHtml(String(solution.votes || 0)) + " votes</span>",
        "</div>",
        "<div class=\"community-solution-body\">" + renderMarkdown(solution.text || "") + "</div>",
        "<button class=\"vote-solution\" type=\"button\" data-solution-id=\"" + escapeHtml(solution.id) + "\"" + (alreadyVoted ? " disabled" : "") + ">",
        alreadyVoted ? "Voted" : "Vote",
        "</button>",
        "</article>"
      ].join("");
    }).join("");
    typesetMath();
  }

  function loadCommunitySolutions(question) {
    var token = state.communityRequestToken + 1;
    state.communityRequestToken = token;
    getElement("community-solutions-list").innerHTML = "<p class=\"muted-note\">Loading proposed solutions...</p>";

    fetch(communityEndpoint(question.id))
      .then(function (response) {
        return response.json().then(function (body) {
          if (!response.ok) {
            throw new Error(body.error || "Could not load proposed solutions.");
          }
          return body;
        });
      })
      .then(function (body) {
        if (token !== state.communityRequestToken) {
          return;
        }
        renderCommunitySolutions(body.solutions || []);
      })
      .catch(function () {
        if (token !== state.communityRequestToken) {
          return;
        }
        getElement("community-solutions-list").innerHTML =
          "<p class=\"muted-note\">Proposed solutions will load once the Netlify function is deployed.</p>";
      });
  }

  function submitSolution() {
    var button = getElement("submit-solution");
    var question = state.activeQuestion;
    var draft = getElement("answer-draft").value.trim();
    if (!question) {
      statusMessage("Load a question first.");
      return;
    }
    if (draft.length < 20) {
      statusMessage("Write a fuller solution before submitting.");
      return;
    }

    button.disabled = true;
    statusMessage("Submitting solution...");

    fetch("/.netlify/functions/community-solutions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "submit",
        questionId: question.id,
        questionTitle: question.title,
        author: getElement("solution-author").value.trim(),
        text: draft
      })
    })
      .then(function (response) {
        return response.json().then(function (body) {
          if (!response.ok) {
            throw new Error(body.error || "Feedback request failed.");
          }
          return body;
        });
      })
      .then(function (body) {
        getElement("answer-draft").value = "";
        getElement("answer-preview").hidden = true;
        getElement("answer-preview").innerHTML = "";
        statusMessage("Solution submitted.");
        renderCommunitySolutions(body.solutions || []);
      })
      .catch(function (error) {
        statusMessage(error.message);
      })
      .finally(function () {
        button.disabled = false;
      });
  }

  function voteOnSolution(solutionId) {
    var question = state.activeQuestion;
    if (!question || !solutionId || hasVoted(question.id, solutionId)) {
      return;
    }
    markVoted(question.id, solutionId);

    fetch("/.netlify/functions/community-solutions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "vote",
        questionId: question.id,
        solutionId: solutionId
      })
    })
      .then(function (response) {
        return response.json().then(function (body) {
          if (!response.ok) {
            throw new Error(body.error || "Could not record vote.");
          }
          return body;
        });
      })
      .then(function (body) {
        renderCommunitySolutions(body.solutions || []);
      })
      .catch(function (error) {
        statusMessage(error.message);
        loadCommunitySolutions(question);
      });
  }

  function initialize() {
    fetch("question_bank_curated/practice-questions.curated.json")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Could not load curated practice questions.");
        }
        return response.json();
      })
      .then(function (questions) {
        state.questions = questions;
        showRandomQuestion();
      })
      .catch(function () {
        getElement("question-title").textContent = "Practice questions are unavailable.";
        getElement("question-prompt").textContent = "The curated question bank could not be loaded.";
      });

    getElement("new-question").addEventListener("click", showRandomQuestion);
    getElement("render-answer").addEventListener("click", renderAnswerDraft);
    getElement("submit-solution").addEventListener("click", submitSolution);
    getElement("community-solutions-list").addEventListener("click", function (event) {
      var button = event.target.closest(".vote-solution");
      if (button) {
        voteOnSolution(button.getAttribute("data-solution-id"));
      }
    });
    getElement("show-hint").addEventListener("click", function () {
      togglePanel("question-hint");
    });
    getElement("show-solution").addEventListener("click", function () {
      togglePanel("question-solution");
    });

    getElement("report-issue-link").addEventListener("click", function () {
      window.setTimeout(function () {
        getElement("issue-description").focus();
      }, 0);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
