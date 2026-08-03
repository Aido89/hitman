// Pricing rules ported 1:1 from the legacy static site's script.js order calculator.
(function () {
  const SERVICE_LABELS = {
    'it-infra': 'Аудит и настройка IT-инфраструктуры',
    streaming: 'Онлайн-трансляция / Студийная съемка',
    training: 'Обучение и тренинги',
    consulting: 'Консалтинг / AI-разработка',
    videography: 'Видеография и фотосъемка',
    repair: 'Ремонт и обслуживание техники',
    webdev: 'Создание сайтов и сервисов',
  };

  const BROADCAST_PRESETS = { party: 80000, podcast: 120000, webinar: 150000, sport: 200000, concert: 250000, forum: 300000, live: 180000, record: 100000 };
  const BROADCAST_LABELS = { party: 'Частная вечеринка', podcast: 'Подкаст', webinar: 'Вебинар', sport: 'Спорт', concert: 'Концерт', forum: 'Форум', live: 'Прямой эфир', record: 'Запись эфира' };
  const TILE_PRICES = { crane: 100000, crane9m: 150000, pavilion: 100000, datavideo: 120000, lens40x: 40000, optics400m: 40000, led: 20000, tele: 20000, lav: 15000, montage: 50000, color: 20000, graphics: 15000 };
  const SHIFT_MULT_TILES = new Set(['crane', 'pavilion', 'crane9m']);
  const IT_OPTION_PRICES = { servers: 80000, network: 60000, security: 100000 };
  const REPAIR_WORK_PRICES = { diagnostic: 5000, 'os-install': 15000, drivers: 5000, software: 10000, optimization: 10000, antivirus: 15000, cleaning: 8000, thermal: 10000 };
  const WEBDEV_OPTION_PRICES = { design: 50000, seo: 40000, integration: 60000, hosting: 30000 };
  const STREAMING_STAFF_PRICES = { sound: 50000, director: 80000 };
  const BASE_PRICES = { 'it-infra': 120000, streaming: 0, training: 90000, consulting: 150000, videography: 0, repair: 15000, webdev: 0 };

  function formatPrice(v) {
    return Math.round(v).toLocaleString('ru-RU') + '₸';
  }

  function readConfig() {
    const form = document.getElementById('order-form');
    const fd = new FormData(form);
    const get = (name, def) => (fd.has(name) ? fd.get(name) : def);
    const getAll = (name) => fd.getAll(name);
    const num = (name, def) => {
      const v = fd.get(name);
      return v === null || v === '' ? def : parseInt(v, 10);
    };
    return {
      serviceType: get('serviceType', 'streaming'),
      urgent: fd.has('urgent'),
      onSite: fd.has('onSite'),
      itInfra: { options: getAll('itOption'), equipment: get('itEquipment', 'with') },
      streaming: {
        preset: get('preset', 'forum'),
        qtyFx3: num('qtyFx3', 0), qtySonyA7: num('qtySonyA7', 0), qtySony500: num('qtySony500', 0),
        qtyHandycam: num('qtyHandycam', 0), qtyPtz: num('qtyPtz', 0),
        tiles: getAll('tile'),
        podcastPkg: get('podcastPkg', 'none'),
        operatorCount: num('operatorCount', 1), shiftCount: num('shiftCount', 1),
        staff: getAll('staff'), outCity: fd.has('outCity'), insurance: fd.has('insurance'),
      },
      training: { format: get('trainingFormat', 'online'), equipment: get('trainingEquipment', 'with') },
      consulting: { equipment: get('consultingEquipment', 'with') },
      videography: { type: get('videographyType', '1cam'), photographer: get('photographer', 'none') },
      repair: { deviceType: get('deviceType', 'pc'), works: getAll('repairWork'), dataRecovery: get('dataRecovery', 'none') },
      webdev: { type: get('webdevType', 'landing'), options: getAll('webdevOption') },
    };
  }

  function calcTotal(c) {
    const breakdown = [];
    let total = 0;
    switch (c.serviceType) {
      case 'it-infra': {
        total = BASE_PRICES['it-infra'];
        breakdown.push(`Базовая стоимость: ${formatPrice(total)}`);
        c.itInfra.options.forEach((opt) => {
          const add = IT_OPTION_PRICES[opt] || 0;
          if (add) { total += add; breakdown.push(`+${formatPrice(add)} (${opt})`); }
        });
        if (c.itInfra.equipment === 'with') { const add = Math.round(total * 0.3); total += add; breakdown.push(`+${formatPrice(add)} (закуп оборудования)`); }
        break;
      }
      case 'streaming': {
        const s = c.streaming;
        const shifts = Math.min(2, Math.max(1, s.shiftCount || 1));
        const numOps = Math.min(8, Math.max(0, s.operatorCount || 0));
        const DAILY_OP = 40000;
        let subtotal = 0;
        const presetPrice = BROADCAST_PRESETS[s.preset];
        if (presetPrice) { subtotal += presetPrice; breakdown.push(`Тип: ${BROADCAST_LABELS[s.preset]} — ${formatPrice(presetPrice)}`); }
        [[s.qtyFx3, 50000, 'Sony FX-3'], [s.qtySonyA7, 30000, 'Sony α7 III'], [s.qtySony500, 30000, 'Sony 500'], [s.qtyHandycam, 15000, 'Sony Handycam'], [s.qtyPtz, 15000, 'PTZ Clever mic']].forEach(([qty, price, label]) => {
          if (qty > 0) { const line = qty * price; subtotal += line; breakdown.push(`${label}: ${qty}×${formatPrice(price)} = ${formatPrice(line)}`); }
        });
        if (numOps > 0) {
          let opLine = numOps * DAILY_OP;
          if (shifts === 2) opLine += Math.round(numOps * DAILY_OP * 1.8);
          subtotal += opLine;
          breakdown.push(`Операторы: ${numOps} чел. × ${shifts} смен(а) — ${formatPrice(opLine)}`);
        }
        s.tiles.forEach((tile) => {
          if (tile === 'rails') { breakdown.push('Рельсы: стоимость по договорённости'); return; }
          const base = TILE_PRICES[tile];
          if (!base) return;
          const price = SHIFT_MULT_TILES.has(tile) ? base * shifts : base;
          subtotal += price;
          breakdown.push(`${tile}: ${formatPrice(price)}`);
        });
        if (s.podcastPkg === 'online') { subtotal += 100000; breakdown.push(`+${formatPrice(100000)} (Podcast онлайн)`); }
        else if (s.podcastPkg === 'with-edit') { subtotal += 150000; breakdown.push(`+${formatPrice(150000)} (Podcast + монтаж)`); }
        s.staff.forEach((staff) => {
          const add = STREAMING_STAFF_PRICES[staff] || 0;
          if (add) { subtotal += add; breakdown.push(`+${formatPrice(add)} (${staff})`); }
        });
        if (s.outCity) { const before = subtotal; subtotal = Math.round(subtotal * 1.2); breakdown.push(`Выезд за город (+20%): ${formatPrice(before)} → ${formatPrice(subtotal)}`); }
        if (s.insurance) { subtotal += 5000; breakdown.push(`+${formatPrice(5000)} (страховка оборудования)`); }
        total = subtotal;
        break;
      }
      case 'training': {
        let base = BASE_PRICES.training;
        if (c.training.format === 'offline') { base = Math.round(base * 1.5); breakdown.push(`Базовая стоимость (офлайн): ${formatPrice(base)}`); }
        else { breakdown.push(`Базовая стоимость (онлайн): ${formatPrice(base)}`); }
        total = base;
        if (c.training.equipment === 'with') { const add = Math.round(total * 0.3); total += add; breakdown.push(`+${formatPrice(add)} (закуп оборудования)`); }
        break;
      }
      case 'consulting': {
        total = BASE_PRICES.consulting;
        breakdown.push(`Базовая стоимость: ${formatPrice(total)}`);
        if (c.consulting.equipment === 'with') { const add = Math.round(total * 0.3); total += add; breakdown.push(`+${formatPrice(add)} (закуп оборудования)`); }
        break;
      }
      case 'videography': {
        if (c.videography.type === '1cam') { total = 100000; breakdown.push(`1 камерная съемка: ${formatPrice(total)}`); }
        else { total = 400000; breakdown.push(`4 камерная съемка: ${formatPrice(total)}`); }
        const photoPrices = { simple: 50000, medium: 75000, complex: 100000 };
        const photoPrice = photoPrices[c.videography.photographer] || 0;
        if (photoPrice) { total += photoPrice; breakdown.push(`+${formatPrice(photoPrice)} (фотограф)`); }
        break;
      }
      case 'repair': {
        total = BASE_PRICES.repair;
        breakdown.push(`Базовая стоимость: ${formatPrice(total)}`);
        if (c.repair.deviceType === 'laptop') { total += 20000; breakdown.push(`+${formatPrice(20000)} (ноутбук)`); }
        else if (c.repair.deviceType === 'monoblock') { total += 30000; breakdown.push(`+${formatPrice(30000)} (моноблок)`); }
        c.repair.works.forEach((w) => { const add = REPAIR_WORK_PRICES[w] || 0; if (add) { total += add; breakdown.push(`+${formatPrice(add)} (${w})`); } });
        if (c.repair.dataRecovery === 'simple') { total += 25000; breakdown.push(`+${formatPrice(25000)} (простое восстановление данных)`); }
        else if (c.repair.dataRecovery === 'complex') { total += 50000; breakdown.push(`+${formatPrice(50000)} (сложное восстановление данных)`); }
        break;
      }
      case 'webdev': {
        const prices = { landing: 150000, corporate: 300000, shop: 500000, portal: 800000, custom: 0 };
        const labels = { landing: 'Лендинг', corporate: 'Корпоративный сайт', shop: 'Интернет-магазин', portal: 'Портал/Веб-приложение', custom: 'Индивидуальный проект' };
        total = prices[c.webdev.type] || 0;
        breakdown.push(c.webdev.type === 'custom' ? 'Индивидуальный проект: цена договорная' : `${labels[c.webdev.type]}: ${formatPrice(total)}`);
        c.webdev.options.forEach((opt) => { const add = WEBDEV_OPTION_PRICES[opt] || 0; if (add) { total += add; breakdown.push(`+${formatPrice(add)} (${opt})`); } });
        break;
      }
    }
    if (c.urgent) { const add = Math.round(total * 0.2); total += add; breakdown.push(`+${formatPrice(add)} (срочный заказ)`); }
    if (c.onSite) { total += 50000; breakdown.push('+' + formatPrice(50000) + ' (выезд/площадка)'); }
    return { total, breakdown };
  }

  function buildWhatsAppUrl(c, total) {
    let msg = `*📋 ЗАЯВКА — Hitman IT*\n\n*Услуга:* ${SERVICE_LABELS[c.serviceType]}\n\n`;
    msg += `\n*Итого:* ${formatPrice(total)}\n\n_Прошу подтвердить детали и слот в графике._`;
    return `https://wa.me/message/VGBVTLQBLHQ7I1?text=${encodeURIComponent(msg)}`;
  }

  function render() {
    const config = readConfig();
    const { total, breakdown } = calcTotal(config);
    document.querySelectorAll('.js-total-price').forEach((el) => { el.textContent = formatPrice(total); });
    document.querySelectorAll('.js-breakdown').forEach((el) => { el.innerHTML = breakdown.join('<br>'); });
    const link = document.getElementById('whatsapp-link');
    if (link) link.href = buildWhatsAppUrl(config, total);
    const totalInput = document.getElementById('id_total');
    const breakdownInput = document.getElementById('id_breakdown');
    const serviceTypeInput = document.getElementById('id_service_type');
    const serviceLabelInput = document.getElementById('id_service_label');
    if (totalInput) totalInput.value = total;
    if (breakdownInput) breakdownInput.value = JSON.stringify(breakdown);
    if (serviceTypeInput) serviceTypeInput.value = config.serviceType;
    if (serviceLabelInput) serviceLabelInput.value = SERVICE_LABELS[config.serviceType];
  }

  function showStep(n) {
    // Funnel event: which step people reach, and where they drop off.
    if (window.track) window.track('smeta_step_' + n);
    document.querySelectorAll('.step-panel').forEach((p) => p.classList.toggle('active', p.dataset.step === String(n)));
    document.querySelectorAll('.step-dot').forEach((d) => d.classList.toggle('active', d.dataset.step === String(n)));
    document.querySelectorAll('.service-fields').forEach((el) => { el.style.display = 'none'; });
    const config = readConfig();
    const activeFields = document.querySelector(`.service-fields[data-service="${config.serviceType}"]`);
    if (activeFields) activeFields.style.display = 'block';
    render();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('order-form');
    if (!form) return;
    form.addEventListener('change', render);
    form.addEventListener('input', render);
    document.querySelectorAll('[data-next]').forEach((btn) => btn.addEventListener('click', () => showStep(btn.dataset.next)));
    // Tiles are <label> elements wrapping a hidden checkbox/radio, so the
    // browser already toggles the input on click via native label behavior —
    // we only need to sync the `.selected` class off the resulting `change`
    // event, not toggle the input ourselves (that double-toggle used to
    // cancel out and make the tiles look unresponsive).
    document.querySelectorAll('.tile-btn input').forEach((input) => {
      input.addEventListener('change', () => {
        if (input.type === 'radio') {
          document.querySelectorAll(`input[name="${input.name}"]`).forEach((sibling) => {
            sibling.closest('.tile-btn').classList.toggle('selected', sibling.checked);
          });
        } else {
          input.closest('.tile-btn').classList.toggle('selected', input.checked);
        }
      });
    });
    showStep('1');
  });
})();
