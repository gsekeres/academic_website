const { randomUUID } = require("node:crypto");

const STORE_NAME = "practice-community-solutions";
const MAX_SOLUTIONS_PER_QUESTION = 100;
const MAX_AUTHOR_LENGTH = 80;
const MAX_TITLE_LENGTH = 300;
const MAX_SOLUTION_LENGTH = 20000;
const MIN_SOLUTION_LENGTH = 20;

function json(statusCode, body) {
  return {
    statusCode,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store"
    },
    body: JSON.stringify(body)
  };
}

function cleanText(value, maxLength) {
  return String(value || "")
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, "")
    .trim()
    .slice(0, maxLength);
}

function validateQuestionId(questionId) {
  const id = cleanText(questionId, 180);
  return /^[A-Za-z0-9._:-]+$/.test(id) ? id : "";
}

function solutionKey(questionId) {
  return `questions/${questionId}.json`;
}

function publicSolution(solution) {
  return {
    id: solution.id,
    author: solution.author || "Anonymous",
    text: solution.text || "",
    votes: Number(solution.votes || 0),
    createdAt: solution.createdAt
  };
}

function sortSolutions(solutions) {
  return solutions
    .map(publicSolution)
    .sort((left, right) => {
      if (right.votes !== left.votes) {
        return right.votes - left.votes;
      }
      return String(left.createdAt).localeCompare(String(right.createdAt));
    });
}

function normalizeEntry(questionId, questionTitle, entry) {
  const source = entry && typeof entry === "object" ? entry : {};
  return {
    questionId,
    questionTitle: cleanText(source.questionTitle || questionTitle, MAX_TITLE_LENGTH),
    solutions: Array.isArray(source.solutions) ? source.solutions.map(publicSolution) : []
  };
}

async function getStore() {
  const blobs = await import("@netlify/blobs");
  return blobs.getStore(STORE_NAME);
}

async function readEntry(store, questionId, questionTitle) {
  const entry = await store.getWithMetadata(solutionKey(questionId), {
    type: "json",
    consistency: "strong"
  });
  if (!entry || !entry.data) {
    return {
      data: normalizeEntry(questionId, questionTitle, null),
      etag: null
    };
  }
  return {
    data: normalizeEntry(questionId, questionTitle, entry.data),
    etag: entry.etag || null
  };
}

async function writeEntry(store, questionId, entry, etag) {
  const options = etag ? { onlyIfMatch: etag } : { onlyIfNew: true };
  return store.setJSON(solutionKey(questionId), entry, options);
}

async function mutateEntry(questionId, questionTitle, mutator) {
  const store = await getStore();
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const current = await readEntry(store, questionId, questionTitle);
    const next = mutator(current.data);
    const result = await writeEntry(store, questionId, next, current.etag);
    if (!result || result.modified !== false) {
      return next;
    }
  }
  throw new Error("Could not save because another update happened at the same time. Try again.");
}

async function listSolutions(event) {
  const questionId = validateQuestionId(event.queryStringParameters && event.queryStringParameters.questionId);
  if (!questionId) {
    return json(400, { error: "Missing or invalid questionId." });
  }

  const store = await getStore();
  const current = await readEntry(store, questionId, "");
  return json(200, {
    questionId,
    solutions: sortSolutions(current.data.solutions)
  });
}

async function submitSolution(payload) {
  const questionId = validateQuestionId(payload.questionId);
  const questionTitle = cleanText(payload.questionTitle, MAX_TITLE_LENGTH);
  const author = cleanText(payload.author, MAX_AUTHOR_LENGTH) || "Anonymous";
  const text = cleanText(payload.text, MAX_SOLUTION_LENGTH);

  if (!questionId) {
    return json(400, { error: "Missing or invalid question id." });
  }
  if (text.length < MIN_SOLUTION_LENGTH) {
    return json(400, { error: "Write a fuller proposed solution before submitting." });
  }

  const now = new Date().toISOString();
  const solution = {
    id: `${Date.now().toString(36)}-${randomUUID().slice(0, 8)}`,
    author,
    text,
    votes: 0,
    createdAt: now
  };

  const entry = await mutateEntry(questionId, questionTitle, (current) => {
    if (current.solutions.length >= MAX_SOLUTIONS_PER_QUESTION) {
      throw new Error("This question already has the maximum number of proposed solutions.");
    }
    return {
      questionId,
      questionTitle: questionTitle || current.questionTitle,
      solutions: current.solutions.concat(solution)
    };
  });

  return json(200, {
    questionId,
    solution,
    solutions: sortSolutions(entry.solutions)
  });
}

async function voteForSolution(payload) {
  const questionId = validateQuestionId(payload.questionId);
  const solutionId = cleanText(payload.solutionId, 80);
  if (!questionId || !solutionId) {
    return json(400, { error: "Missing question id or solution id." });
  }

  let found = false;
  const entry = await mutateEntry(questionId, "", (current) => {
    return {
      questionId,
      questionTitle: current.questionTitle,
      solutions: current.solutions.map((solution) => {
        if (solution.id !== solutionId) {
          return solution;
        }
        found = true;
        return {
          ...solution,
          votes: Number(solution.votes || 0) + 1
        };
      })
    };
  });

  if (!found) {
    return json(404, { error: "Could not find that proposed solution." });
  }

  return json(200, {
    questionId,
    solutions: sortSolutions(entry.solutions)
  });
}

exports.handler = async function handler(event) {
  if (event.httpMethod === "GET") {
    return listSolutions(event);
  }
  if (event.httpMethod !== "POST") {
    return json(405, { error: "Use GET or POST." });
  }

  let payload;
  try {
    payload = JSON.parse(event.body || "{}");
  } catch {
    return json(400, { error: "Request body must be valid JSON." });
  }

  try {
    if (payload.action === "submit") {
      return submitSolution(payload);
    }
    if (payload.action === "vote") {
      return voteForSolution(payload);
    }
  } catch (error) {
    return json(409, { error: error.message || "Could not save this update." });
  }

  return json(400, { error: "Unknown action." });
};
