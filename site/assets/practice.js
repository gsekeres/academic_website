(function () {
  var state = {
    questions: [],
    activeQuestion: null
  };

  function getElement(id) {
    return document.getElementById(id);
  }

  function pickQuestion() {
    if (!state.questions.length) {
      return null;
    }
    var index = Math.floor(Math.random() * state.questions.length);
    return state.questions[index];
  }

  function renderTags(question) {
    var tags = [question.source_family, question.difficulty].concat(question.topics || []);
    return tags
      .filter(Boolean)
      .map(function (tag) {
        return "<span>" + tag + "</span>";
      })
      .join("");
  }

  function renderQuestion(question) {
    state.activeQuestion = question;
    getElement("question-title").textContent = question.title;
    getElement("question-meta").innerHTML = renderTags(question);
    getElement("question-prompt").innerHTML = question.prompt;
    getElement("question-hint").hidden = true;
    getElement("question-solution").hidden = true;
    getElement("question-hint").innerHTML = question.hint;
    getElement("question-solution").innerHTML = question.solution;
    getElement("answer-draft").value = "";
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
  }

  function initialize() {
    fetch("/assets/practice-questions.json")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Could not load practice questions.");
        }
        return response.json();
      })
      .then(function (questions) {
        state.questions = questions;
        showRandomQuestion();
      })
      .catch(function () {
        getElement("question-title").textContent = "Practice questions are unavailable.";
        getElement("question-prompt").textContent = "The question bank could not be loaded.";
      });

    getElement("new-question").addEventListener("click", showRandomQuestion);
    getElement("show-hint").addEventListener("click", function () {
      togglePanel("question-hint");
    });
    getElement("show-solution").addEventListener("click", function () {
      togglePanel("question-solution");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
