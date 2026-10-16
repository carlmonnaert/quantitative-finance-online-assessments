const DEFAULT_CONFIG = {
  durationMinutes: 15,
  targetQuestionCount: 30,
};

const state = {
  config: { ...DEFAULT_CONFIG },
  questions: [],
  selectedQuestions: [],
  currentIndex: 0,
  answers: {},
  timerInterval: null,
  remainingSeconds: 15 * 60,
  startedAt: null,
  submitted: false,
};

const elements = {
  questionNav: document.getElementById('questionNav'),
  questionProgress: document.getElementById('questionProgress'),
  timer: document.getElementById('timer'),
  questionContainer: document.getElementById('questionContainer'),
  emptyState: document.getElementById('emptyState'),
  questionTitle: document.getElementById('questionTitle'),
  questionPrompt: document.getElementById('questionPrompt'),
  choices: document.getElementById('choices'),
  freeResponse: document.getElementById('freeResponse'),
  responseInput: document.getElementById('responseInput'),
  responseLabel: document.getElementById('responseLabel'),
  prevBtn: document.getElementById('prevBtn'),
  nextBtn: document.getElementById('nextBtn'),
  submitBtn: document.getElementById('submitBtn'),
  summaryDialog: document.getElementById('summaryDialog'),
  summaryText: document.getElementById('summaryText'),
  summaryReport: document.getElementById('summaryReport'),
  closeSummary: document.getElementById('closeSummary'),
};

function shuffle(array) {
  const copy = [...array];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[randomIndex]] = [copy[randomIndex], copy[index]];
  }
  return copy;
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function isAnswered(questionId) {
  const value = state.answers[questionId];
  if (value === undefined || value === null) {
    return false;
  }
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return true;
}

function updateTimerView() {
  elements.timer.textContent = formatTime(state.remainingSeconds);
}

function updateProgressView() {
  const total = state.selectedQuestions.length;
  const current = total === 0 ? 0 : state.currentIndex + 1;
  elements.questionProgress.textContent = `Question ${current} / ${total}`;
}

function renderNav() {
  elements.questionNav.innerHTML = '';
  state.selectedQuestions.forEach((question, index) => {
    const button = document.createElement('button');
    button.className = 'nav-btn';
    button.textContent = `${index + 1}`;

    if (index === state.currentIndex) {
      button.classList.add('active');
    }
    if (isAnswered(question.id)) {
      button.classList.add('answered');
    }

    button.addEventListener('click', () => {
      state.currentIndex = index;
      renderCurrentQuestion();
    });
    elements.questionNav.appendChild(button);
  });
}

function handleMcqSelection(questionId, optionValue) {
  state.answers[questionId] = optionValue;
  renderNav();
}

function handleTextResponse(questionId, event) {
  state.answers[questionId] = event.target.value;
  renderNav();
}

function renderCurrentQuestion() {
  const question = state.selectedQuestions[state.currentIndex];
  updateProgressView();
  renderNav();

  if (!question) {
    elements.questionContainer.classList.add('hidden');
    elements.emptyState.classList.remove('hidden');
    return;
  }

  elements.emptyState.classList.add('hidden');
  elements.questionContainer.classList.remove('hidden');

  elements.questionTitle.textContent = `${state.currentIndex + 1}. ${question.title}`;
  elements.questionPrompt.textContent = question.prompt;

  elements.choices.innerHTML = '';
  elements.freeResponse.classList.add('hidden');

  if (question.type === 'mcq') {
    question.options.forEach((option) => {
      const wrapper = document.createElement('label');
      wrapper.className = 'choice';

      const input = document.createElement('input');
      input.type = 'radio';
      input.name = `question-${question.id}`;
      input.value = option.value;
      input.checked = state.answers[question.id] === option.value;
      input.addEventListener('change', () => handleMcqSelection(question.id, option.value));

      const text = document.createElement('span');
      text.textContent = ` ${option.label}`;

      wrapper.appendChild(input);
      wrapper.appendChild(text);
      elements.choices.appendChild(wrapper);
    });
  } else {
    elements.freeResponse.classList.remove('hidden');
    elements.responseLabel.textContent = question.type === 'numeric' ? 'Numeric answer' : 'Answer';
    elements.responseInput.value = state.answers[question.id] ?? '';
    elements.responseInput.placeholder = question.type === 'numeric' ? 'e.g., 0.73' : 'Type your answer';
    elements.responseInput.oninput = (event) => handleTextResponse(question.id, event);
  }

  elements.prevBtn.disabled = state.currentIndex === 0;
  elements.nextBtn.disabled = state.currentIndex >= state.selectedQuestions.length - 1;
}

function isCorrectAnswer(question, userRaw) {
  if (userRaw === undefined || userRaw === null || question.answer === undefined) {
    return false;
  }
  const userStr = String(userRaw).trim();
  const targetStr = String(question.answer).trim();

  if (question.type === 'numeric') {
    const uVal = Number(userStr);
    const tVal = Number(targetStr);
    if (!Number.isNaN(uVal) && !Number.isNaN(tVal)) {
      return Math.abs(uVal - tVal) <= 1e-4;
    }
  }
  return userStr.toLowerCase() === targetStr.toLowerCase();
}

function formatAnswerForDisplay(question, rawValue) {
  if (rawValue === undefined || rawValue === null) {
    return '—';
  }

  const normalized = String(rawValue).trim();
  if (normalized.length === 0) {
    return '—';
  }

  if (question.type === 'mcq' && Array.isArray(question.options)) {
    const matchedOption = question.options.find((option) => option.value === normalized);
    if (matchedOption) {
      return `${matchedOption.value} (${matchedOption.label})`;
    }
  }

  return normalized;
}

function renderSubmissionReport(results) {
  elements.summaryReport.innerHTML = '';

  const addMetaLine = (container, label, value) => {
    const row = document.createElement('p');
    row.className = 'report-meta';

    const strong = document.createElement('strong');
    strong.textContent = `${label}:`;

    const text = document.createTextNode(` ${value}`);
    row.appendChild(strong);
    row.appendChild(text);
    container.appendChild(row);
  };

  results.forEach((result) => {
    const item = document.createElement('article');
    item.className = `report-item ${result.isCorrect ? 'correct' : 'incorrect'}`;

    const title = document.createElement('p');
    title.className = 'report-title';
    title.textContent = `Q${result.questionNumber}: ${result.title}`;

    item.appendChild(title);
    addMetaLine(item, 'Result', `${result.isCorrect ? 'Correct' : 'Incorrect'} | Score: ${result.points}/1`);
    addMetaLine(item, 'Your answer', result.userAnswerDisplay);
    addMetaLine(item, 'Correct answer', result.correctAnswerDisplay);
    addMetaLine(item, 'Explanation', result.explanation);
    elements.summaryReport.appendChild(item);
  });
}

function submitTest(reason = 'manual') {
  if (state.submitted) {
    return;
  }
  state.submitted = true;
  clearInterval(state.timerInterval);

  const totalQuestions = state.selectedQuestions.length;

  const results = state.selectedQuestions.map((question, index) => {
    const userRaw = state.answers[question.id];
    const answered = isAnswered(question.id);
    const isCorrect = isCorrectAnswer(question, userRaw);
    return {
      questionNumber: index + 1,
      title: question.title,
      isCorrect,
      points: isCorrect ? 1 : 0,
      answered,
      userAnswerDisplay: formatAnswerForDisplay(question, userRaw),
      correctAnswerDisplay: formatAnswerForDisplay(question, question.answer),
      explanation: question.explanation ?? 'No explanation provided.',
    };
  });

  const answeredCount = results.filter((result) => result.answered).length;
  const correctCount = results.filter((result) => result.isCorrect).length;
  const unanswered = totalQuestions - answeredCount;

  elements.summaryText.textContent =
    `Submission reason: ${reason}. ` +
    `Score: ${correctCount} / ${totalQuestions} (${Math.round((correctCount / (totalQuestions || 1)) * 100)}%). ` +
    `Answered: ${answeredCount}, Unanswered: ${unanswered}.`;
  renderSubmissionReport(results);
  elements.summaryDialog.showModal();

  elements.prevBtn.disabled = true;
  elements.nextBtn.disabled = true;
  elements.submitBtn.disabled = true;
}

function startTimer() {
  updateTimerView();
  state.startedAt = new Date();
  state.timerInterval = setInterval(() => {
    state.remainingSeconds -= 1;
    updateTimerView();

    if (state.remainingSeconds <= 0) {
      state.remainingSeconds = 0;
      updateTimerView();
      submitTest('time_expired');
    }
  }, 1000);
}

// 1-based question numbers that must be "Complete" (numeric / text) questions:
// Q4; Q11 - Q12; Q16; Q21 - Q22; Q25
// All remaining slots (Q1-Q3; Q5-Q10; Q13-Q15; Q17-Q20; Q23-Q24; Q26-Q30) are MCQ.
const COMPLETE_QUESTION_NUMBERS = new Set([4, 11, 12, 16, 21, 22, 25]);

function buildStructuredQuestionList(allQuestions, targetCount) {
  // Deduplicate by question id so no question ever appears twice
  const seenIds = new Set();
  const uniqueQuestions = [];
  for (const q of allQuestions) {
    if (q && q.id && !seenIds.has(q.id)) {
      seenIds.add(q.id);
      uniqueQuestions.push(q);
    }
  }

  const mcqPool = shuffle(uniqueQuestions.filter((q) => q.type === 'mcq'));
  const completePool = shuffle(uniqueQuestions.filter((q) => q.type !== 'mcq'));

  const selected = [];
  let mcqIndex = 0;
  let completeIndex = 0;

  for (let qNum = 1; qNum <= targetCount; qNum += 1) {
    const wantsComplete = COMPLETE_QUESTION_NUMBERS.has(qNum);

    if (wantsComplete && completeIndex < completePool.length) {
      selected.push(completePool[completeIndex]);
      completeIndex += 1;
    } else if (!wantsComplete && mcqIndex < mcqPool.length) {
      selected.push(mcqPool[mcqIndex]);
      mcqIndex += 1;
    } else if (mcqIndex < mcqPool.length) {
      // Fallback if one pool is exhausted
      selected.push(mcqPool[mcqIndex]);
      mcqIndex += 1;
    } else if (completeIndex < completePool.length) {
      selected.push(completePool[completeIndex]);
      completeIndex += 1;
    }
  }

  return selected;
}

async function loadQuestionsFromManifest() {
  const manifestResponse = await fetch('./question-bank/manifest.json');
  if (!manifestResponse.ok) {
    throw new Error('Unable to read question-bank/manifest.json');
  }

  const manifest = await manifestResponse.json();
  state.config = {
    ...DEFAULT_CONFIG,
    ...(manifest.assessmentConfig ?? {}),
  };
  state.remainingSeconds = state.config.durationMinutes * 60;

  if (!Array.isArray(manifest.files)) {
    throw new Error('manifest.files must be an array of JSON file paths');
  }

  const loadedQuestions = [];
  for (const relativePath of manifest.files) {
    const fileResponse = await fetch(`./question-bank/questions/${relativePath}`);
    if (!fileResponse.ok) {
      throw new Error(`Unable to load question file: ${relativePath}`);
    }

    const questionSet = await fileResponse.json();
    if (!Array.isArray(questionSet.questions)) {
      throw new Error(`Question file ${relativePath} must include a 'questions' array`);
    }

    loadedQuestions.push(...questionSet.questions);
  }

  state.questions = loadedQuestions;
  state.selectedQuestions = buildStructuredQuestionList(
    state.questions,
    state.config.targetQuestionCount
  );

  if (state.selectedQuestions.length === 0) {
    elements.emptyState.classList.remove('hidden');
    elements.questionContainer.classList.add('hidden');
  }
}

function wireEvents() {
  elements.prevBtn.addEventListener('click', () => {
    if (state.currentIndex > 0) {
      state.currentIndex -= 1;
      renderCurrentQuestion();
    }
  });

  elements.nextBtn.addEventListener('click', () => {
    if (state.currentIndex < state.selectedQuestions.length - 1) {
      state.currentIndex += 1;
      renderCurrentQuestion();
    }
  });

  elements.submitBtn.addEventListener('click', () => submitTest('manual'));
  elements.closeSummary.addEventListener('click', () => elements.summaryDialog.close());
}

async function bootstrap() {
  wireEvents();
  try {
    await loadQuestionsFromManifest();
  } catch (error) {
    elements.emptyState.classList.remove('hidden');
    elements.questionContainer.classList.add('hidden');
    elements.emptyState.innerHTML = `<h2>Could not load question bank</h2><p>${error.message}</p>`;
  }

  updateTimerView();
  updateProgressView();
  renderNav();
  renderCurrentQuestion();
  startTimer();
}

bootstrap();
