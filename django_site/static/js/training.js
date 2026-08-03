(function () {
  const UI = {
    ru: { goal: 'Цель', practice: 'Практическое задание', interactive: 'Интерактив', assignment: 'Задание', case_: 'Кейс', video: 'Видео по теме', test: '🧠 Мини-тест: проверка знаний', check: 'Проверить ответ', correct: '✅ Правильно! Идём дальше.', wrong: '❌ Неверно. Попробуйте ещё раз.', empty: 'Пожалуйста, выберите один из вариантов ответа.', modules: 'Модули', tests: 'Тесты', mainTitle: 'Основы работы с Google Workspace (Расширенный курс)', mainSubtitle: 'Модуль I. Интерактивное знакомство с цифровой экосистемой' },
    kk: { goal: 'Мақсат', practice: 'Практикалық тапсырма', interactive: 'Интерактив', assignment: 'Тапсырма', case_: 'Кейс', video: 'Тақырыптық бейне', test: '🧠 Мини-тест: білімді тексеру', check: 'Жауапты тексеру', correct: '✅ Дұрыс! Алға жылжимыз.', wrong: '❌ Қате. Қайта көріңіз.', empty: 'Жауап нұсқаларының бірін таңдаңыз.', modules: 'Модульдер', tests: 'Тесттер', mainTitle: 'Google Workspace-пен жұмыс негіздері (Кеңейтілген курс)', mainSubtitle: 'I модуль. Сандық экожүйемен интерактивті танысу' },
  };

  let lang = 'ru';
  let activeId = 0;
  const visited = new Set([0]);
  const correctTests = new Set();
  const modules = window.COURSE_DATA || [];

  function findModule(id) {
    return modules.find((m) => m.id === id);
  }

  function renderNav() {
    const nav = document.getElementById('module-nav');
    nav.innerHTML = modules.map((m) => `
      <li>
        <button type="button" data-id="${m.id}" style="width:100%;text-align:left;background:${m.id === activeId ? 'rgba(220,38,38,0.15)' : 'transparent'};color:${m.id === activeId ? 'var(--red)' : 'var(--text-dim)'};border:none;padding:0.5rem 0.6rem;border-radius:0.5rem;cursor:pointer;font-size:0.85rem;display:flex;gap:0.5rem;align-items:center">
          <span>${m.icon}</span><span>${m.title[lang]}</span>
        </button>
      </li>
    `).join('');
    nav.querySelectorAll('button').forEach((btn) => btn.addEventListener('click', () => selectModule(parseInt(btn.dataset.id, 10))));
  }

  function selectModule(id) {
    activeId = id;
    visited.add(id);
    renderNav();
    renderModule();
    updateProgress();
  }

  function renderModule() {
    const m = findModule(activeId);
    const c = m.content[lang];
    const t = UI[lang];
    const practiceItems = c.practice.map((item, i) => `<li style="margin-bottom:0.5rem"><strong class="text-red">${i + 1}.</strong> ${item}</li>`).join('');
    document.getElementById('module-content').innerHTML = `
      <h2 style="display:flex;gap:0.5rem;align-items:center"><span>${m.icon}</span>${m.title[lang]}</h2>
      <div class="card" style="background:rgba(220,38,38,0.06);border-color:var(--border-red)"><h4 class="text-red">${t.goal}</h4><p>${c.goal}</p></div>
      <div class="card" style="background:var(--card-alt)"><h4>${t.practice}</h4><ol style="padding-left:1rem;margin:0">${practiceItems}</ol></div>
      <div class="card" style="background:rgba(234,179,8,0.08);border-color:rgba(161,98,7,0.4)"><h4 style="color:#fbbf24">${t.interactive}</h4><p>${c.interactive}</p></div>
      <div class="card" style="background:rgba(220,38,38,0.06)"><h4 class="text-red">${t.assignment}</h4><p>${c.assignment}</p></div>
      <div class="card" style="background:var(--card-alt)"><h4>${t.case_}</h4><p>${c.case}</p></div>
      ${c.video ? `<div class="card"><h4>${t.video}</h4><div style="position:relative;padding-top:56.25%;border-radius:0.75rem;overflow:hidden"><iframe src="${c.video}" style="position:absolute;inset:0;width:100%;height:100%" allowfullscreen></iframe></div></div>` : ''}
      <div class="card" style="background:var(--card-alt)">
        <h3>${t.test}</h3>
        <p>${c.quiz.q}</p>
        <form id="quiz-form">
          ${c.quiz.options.map((opt, i) => `<label style="display:block;margin-bottom:0.4rem"><input type="radio" name="answer" value="${i}"> ${opt}</label>`).join('')}
          <button type="button" class="btn btn-primary" id="check-btn" style="margin-top:0.75rem">${t.check}</button>
        </form>
        <p id="quiz-feedback" style="margin-top:0.75rem;font-weight:700"></p>
      </div>
    `;
    document.getElementById('check-btn').addEventListener('click', () => checkAnswer(m, c));
  }

  function checkAnswer(m, c) {
    const form = document.getElementById('quiz-form');
    const selected = form.querySelector('input[name="answer"]:checked');
    const feedback = document.getElementById('quiz-feedback');
    const t = UI[lang];
    if (!selected) { feedback.textContent = t.empty; feedback.style.color = '#fbbf24'; return; }
    const isCorrect = parseInt(selected.value, 10) === c.quiz.correct;
    if (isCorrect) { correctTests.add(m.id); feedback.textContent = t.correct; feedback.style.color = '#4ade80'; }
    else { feedback.textContent = t.wrong; feedback.style.color = '#dc2626'; }
    updateProgress();
  }

  function updateProgress() {
    const total = modules.length;
    const pct = Math.round((visited.size / total) * 100);
    const testsPct = Math.round((correctTests.size / total) * 100);
    const circumference = 2 * Math.PI * 42;
    const ring = document.getElementById('progress-ring');
    ring.setAttribute('stroke-dasharray', circumference);
    ring.setAttribute('stroke-dashoffset', circumference - (pct / 100) * circumference);
    document.getElementById('progress-text').textContent = pct + '%';
    document.getElementById('tests-text').textContent = `${UI[lang].tests}: ${correctTests.size}/${total} (${testsPct}%)`;
  }

  function renderBonus() {
    const ideas = (window.BONUS_IDEAS || {})[lang] || [];
    document.getElementById('bonus-content').innerHTML = ideas.map((i) => `<div class="card" style="background:var(--card-alt);margin-top:0.5rem">${i}</div>`).join('');
  }

  function renderMaterials() {
    const ids = window.MATERIALS_IDS || [];
    document.getElementById('materials-list').innerHTML = ids.map((id) => {
      const m = findModule(id);
      if (!m) return '';
      return `<button type="button" class="btn btn-ghost" style="justify-content:flex-start" onclick="window.scrollTo({top:0,behavior:'smooth'});document.querySelector('[data-id=\\'${id}\\']').click()">${m.icon} ${m.title[lang]}</button>`;
    }).join('');
  }

  function setLang(l) {
    lang = l;
    document.getElementById('course-title').textContent = UI[lang].mainTitle;
    document.getElementById('course-subtitle').textContent = UI[lang].mainSubtitle;
    renderNav();
    renderModule();
    updateProgress();
    renderBonus();
    renderMaterials();
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-lang]').forEach((btn) => btn.addEventListener('click', () => setLang(btn.dataset.lang)));
    setLang('ru');
  });
})();
