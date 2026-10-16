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

function submitTest(reason = 'manual') {
  if (state.submitted) {
    return;
  }
  state.submitted = true;
  clearInterval(state.timerInterval);

  const totalQuestions = state.selectedQuestions.length;
  const answeredCount = state.selectedQuestions.filter((question) => isAnswered(question.id)).length;
  const unanswered = totalQuestions - answeredCount;

  elements.summaryText.textContent = `Submission reason: ${reason}. Answered ${answeredCount} of ${totalQuestions} questions. Unanswered: ${unanswered}.`;
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

  const randomized = shuffle(state.questions);
  state.selectedQuestions = randomized.slice(0, state.config.targetQuestionCount);

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
