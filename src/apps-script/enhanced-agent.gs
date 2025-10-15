// ========== ENHANCED AI AGENT FOR GOOGLE SHEETS ==========
// Этап 1: Подсветка отклонений + предложение решений
// Этап 2: Управление предложениями из созвонов
// Этап 3: Применение решений (по апруву)

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 AI Агент')
    .addItem('🔧 Настройка схемы', 'setupSchema')
    .addItem('📊 Сканировать сигналы', 'scanSignals')
    .addItem('📋 Панель управления', 'showSidebar')
    .addItem('⚙️ Добавить правила', 'addStarterRules')
    .addItem('🔄 Настроить расписание', 'setupTriggers')
    .addItem('📈 Саммари изменений', 'generateSummary')
    .addToUi();
}

// ========== КОНФИГУРАЦИЯ ==========
const CONFIG = {
  // Автоматическое определение листов с данными по названию
  dataSheetPattern: /^(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)\s+\d{4}$/i,
  headerRow: 1,
  metricNameCol: 1, // колонка A
  dateStartCol: 3,  // колонка C (данные начинаются с C)
  rollingWindowDays: 7,
  minSamplesDefault: 5,
  highlight: { 
    bg: '#fff3cd', 
    notePrefix: 'AI Агент: ',
    high: '#ffebee',
    medium: '#fff3e0',
    low: '#e8f5e8'
  }
};

// ========== АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ ЛИСТОВ ==========
function findDataSheets() {
  const ss = SpreadsheetApp.getActive();
  const sheets = ss.getSheets();
  const dataSheets = [];
  
  sheets.forEach(sheet => {
    const sheetName = sheet.getName();
    if (CONFIG.dataSheetPattern.test(sheetName)) {
      dataSheets.push(sheetName);
    }
  });
  
  return dataSheets;
}

// ========== НАСТРОЙКА СХЕМЫ ==========
function setupSchema() {
  const ss = SpreadsheetApp.getActive();
  
  // Создаем/проверяем листы
  ensureSheetWithHeader(ss, 'Algorithm', [
    'RuleId', 'Block', 'Metric', 'ConditionType', 'ConditionParams', 'ActionType', 'ActionParams', 'Severity', 'AutoApply', 'Active', 'CreatedAt', 'Notes'
  ]);
  
  ensureSheetWithHeader(ss, 'Signals', [
    'Timestamp', 'Block', 'Metric', 'Date', 'CurrentValue', 'BaselineValue', 'DeltaPct', 'RuleId', 'Status', 'LinkToCell', 'Severity'
  ]);
  
  ensureSheetWithHeader(ss, 'Decisions', [
    'SignalId', 'SuggestedActionType', 'ActionParams', 'Rationale', 'Status', 'ApprovedBy', 'AppliedAt', 'AuditLog', 'Confidence'
  ]);
  
  ensureSheetWithHeader(ss, 'Изменения', [
    'Timestamp', 'Action', 'Description', 'Result', 'User', 'Status'
  ]);
  
  ensureSheetWithHeader(ss, 'Proposals', [
    'CallDate','ExtractedCase','ExistingRuleMatched','SuggestedRuleDiff','Confidence','Status','Notes','RuleId'
  ]);
  
  SpreadsheetApp.getUi().alert('✅ Готово: созданы/проверены все листы схемы');
}

// ========== СТАРТОВЫЕ ПРАВИЛА ==========
function addStarterRules() {
  const ss = SpreadsheetApp.getActive();
  const algorithmSheet = ss.getSheetByName('Algorithm');
  if (!algorithmSheet) {
    SpreadsheetApp.getUi().alert('❌ Сначала создайте схему (Настройка схемы)');
    return;
  }
  
  const starterRules = [
    ['R001','funnel','Конверсия в корзину, %','ratio','{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}','price_adjust','{"competitor_scan":"on","target_delta_pct":"match_top3-1%","floor_margin_pct":12}','high','N','Y',new Date().toISOString(),'Автоматически добавлено'],
    ['R002','ads','CTR','ratio','{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}','content_ticket','{"task":"replace_main_image","priority":"high","assignee":"content_manager"}','medium','N','Y',new Date().toISOString(),'Автоматически добавлено'],
    ['R003','funnel','Переходы в карточку','ratio','{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}','ads_bid_adjust','{"target":"clicks","delta":"-10% to +10%","guard":"acos<=0.3"}','medium','N','Y',new Date().toISOString(),'Автоматически добавлено'],
    ['R004','funnel','Положили в корзину','ratio','{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}','price_adjust','{"competitor_scan":"on","target_delta_pct":"match_top3-2%","floor_margin_pct":10}','high','N','Y',new Date().toISOString(),'Автоматически добавлено'],
    ['R005','funnel','CR','ratio','{"baseline":"rolling_7d","drop_pct":0.1,"min_samples":5}','content_ticket','{"task":"review_product_description","priority":"high","assignee":"content_manager"}','high','N','Y',new Date().toISOString(),'Автоматически добавлено'],
    ['R006','ads','Показы','ratio','{"baseline":"rolling_7d","drop_pct":0.3,"min_samples":5}','ads_budget_adjust','{"target":"impressions","delta":"+20%","max_budget_increase":5000}','low','N','Y',new Date().toISOString(),'Автоматически добавлено']
  ];
  
  // Проверяем, есть ли уже правила
  const lastRow = algorithmSheet.getLastRow();
  if (lastRow > 1) {
    const response = SpreadsheetApp.getUi().alert(
      'Внимание', 
      'В листе Algorithm уже есть данные. Добавить стартовые правила?', 
      SpreadsheetApp.getUi().ButtonSet.YES_NO
    );
    if (response !== SpreadsheetApp.getUi().Button.YES) return;
  }
  
  // Добавляем правила
  const startRow = lastRow > 1 ? lastRow + 1 : 2;
  algorithmSheet.getRange(startRow, 1, starterRules.length, starterRules[0].length).setValues(starterRules);
  
  SpreadsheetApp.getUi().alert(`✅ Добавлено ${starterRules.length} стартовых правил`);
}

// ========== СКАНИРОВАНИЕ СИГНАЛОВ ==========
function scanSignals() {
  const ss = SpreadsheetApp.getActive();
  const algorithmSheet = ss.getSheetByName('Algorithm');
  const signalsSheet = ss.getSheetByName('Signals');
  const decisionsSheet = ss.getSheetByName('Decisions');
  const changesSheet = ss.getSheetByName('Изменения');
  
  if (!algorithmSheet || !signalsSheet || !decisionsSheet) {
    SpreadsheetApp.getUi().alert('Ошибка: Сначала создайте схему (Настройка схемы)');
    return;
  }
  
  const algorithm = readAlgorithm(algorithmSheet);
  if (algorithm.length === 0) {
    SpreadsheetApp.getUi().alert('Ошибка: Нет активных правил в листе Algorithm');
    return;
  }
  
  // Находим листы с данными автоматически
  const dataSheets = findDataSheets();
  if (dataSheets.length === 0) {
    SpreadsheetApp.getUi().alert('Ошибка: Не найдены листы с данными (формат: "Месяц Год")');
    return;
  }
  
  const nowIso = new Date().toISOString();
  let signalsCount = 0;
  let totalSignals = [];
  
  dataSheets.forEach(name => {
    const sheet = ss.getSheetByName(name);
    if (!sheet) return;
    
    const lastDateCol = findLastDateColumn(sheet);
    if (!lastDateCol) return;
    
    const todayDate = sheet.getRange(CONFIG.headerRow, lastDateCol).getValue();
    const baselineCols = rangeBack(lastDateCol - 1, CONFIG.rollingWindowDays, CONFIG.dateStartCol);
    if (baselineCols.length === 0) return;
    
    const lastRow = sheet.getLastRow();
    for (let r = CONFIG.headerRow + 1; r <= lastRow; r++) {
      const metricName = sheet.getRange(r, CONFIG.metricNameCol).getDisplayValue().trim();
      if (!metricName) continue;
      
      const currentValue = toNumberSafe(sheet.getRange(r, lastDateCol).getValue());
      const baselineValues = baselineCols.map(c => toNumberSafe(sheet.getRange(r, c).getValue()))
        .filter(v => isFinite(v));
      
      if (baselineValues.length < CONFIG.minSamplesDefault) continue;
      
      const baseline = avg(baselineValues);
      const deltaPct = computeDeltaPct(currentValue, baseline);
      
      const rule = matchRule(algorithm, metricName, { currentValue, baseline, deltaPct, samples: baselineValues.length });
      if (!rule) continue;
      
      // Записываем сигнал
      const link = makeA1NotationLink_(ss, sheet, r, lastDateCol);
      const signalId = appendRow_(signalsSheet, [
        nowIso,
        rule.Block,
        metricName,
        formatDate_(todayDate),
        currentValue,
        baseline,
        deltaPct,
        rule.RuleId,
        'new',
        link,
        rule.Severity
      ]);
      
      // Записываем решение
      const rationale = `📉 Падение на ${(deltaPct*100).toFixed(1)}% vs ${CONFIG.rollingWindowDays}д база; правило: ${rule.RuleId}`;
      appendRow_(decisionsSheet, [
        signalId,
        rule.ActionType,
        rule.ActionParamsRaw || '',
        rationale,
        'pending',
        '',
        '',
        '',
        0.8 // confidence
      ]);
      
      // Подсвечиваем ячейку
      highlightCellWithNote_(sheet, r, lastDateCol, rule, rationale);
      signalsCount++;
      
      // Добавляем сигнал в общий список
      totalSignals.push({
        sheet: name,
        metric: metricName,
        value: currentValue,
        baseline: baseline,
        delta: deltaPct,
        rule: rule.RuleId
      });
    }
  });
  
  // Записываем в журнал изменений
  if (changesSheet) {
    const changesDescription = `Сканирование завершено. Найдено ${signalsCount} сигналов в листах: ${dataSheets.join(', ')}. ` +
      `Источники: ${totalSignals.map(s => `${s.sheet}!${s.metric} (${s.delta.toFixed(1)}%)`).join(', ')}`;
    
    changesSheet.appendRow([
      nowIso,
      'Сканирование сигналов',
      changesDescription,
      signalsCount > 0 ? 'Найдены отклонения' : 'Отклонений не найдено',
      'AI Агент',
      'Завершено'
    ]);
  }
  
  SpreadsheetApp.getUi().alert(`Сканирование завершено: найдено ${signalsCount} сигналов в ${dataSheets.length} листах`);
}

// ========== БОКОВАЯ ПАНЕЛЬ ==========
function showSidebar() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #4285f4; color: white; padding: 15px; margin: -20px -20px 20px -20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .button { background: #4285f4; color: white; border: none; padding: 10px 15px; border-radius: 3px; cursor: pointer; margin: 5px; }
        .button:hover { background: #3367d6; }
        .button.danger { background: #ea4335; }
        .button.success { background: #34a853; }
        .status { padding: 5px 10px; border-radius: 3px; margin: 5px 0; }
        .status.pending { background: #fff3cd; }
        .status.approved { background: #d4edda; }
        .status.rejected { background: #f8d7da; }
        .metric { font-weight: bold; color: #1a73e8; }
        .action { color: #137333; }
      </style>
    </head>
    <body>
      <div class="header">
        <h2>🤖 AI Agent - Панель управления</h2>
      </div>
      
      <div class="section">
        <h3>📊 Быстрые действия</h3>
        <button class="button" onclick="scanSignals()">Сканировать сигналы</button>
        <button class="button" onclick="refreshData()">Обновить данные</button>
        <button class="button" onclick="clearHighlights()">Очистить подсветки</button>
      </div>
      
      <div class="section">
        <h3>📋 Последние решения (pending)</h3>
        <div id="decisionsList">Загрузка...</div>
      </div>
      
      <div class="section">
        <h3>💡 Предложения из созвонов</h3>
        <div id="proposalsList">Загрузка...</div>
      </div>
      
      <script>
        function scanSignals() {
          google.script.run
            .withSuccessHandler(() => {
              alert('Сканирование завершено');
              refreshData();
            })
            .withFailureHandler(err => alert('Ошибка: ' + err.message))
            .scanSignals();
        }
        
        function refreshData() {
          loadDecisions();
          loadProposals();
        }
        
        function loadDecisions() {
          google.script.run
            .withSuccessHandler(displayDecisions)
            .withFailureHandler(err => document.getElementById('decisionsList').innerHTML = 'Ошибка загрузки')
            .getPendingDecisions();
        }
        
        function loadProposals() {
          google.script.run
            .withSuccessHandler(displayProposals)
            .withFailureHandler(err => document.getElementById('proposalsList').innerHTML = 'Ошибка загрузки')
            .getPendingProposals();
        }
        
        function displayDecisions(decisions) {
          const html = decisions.length === 0 ? 'Нет pending решений' : 
            decisions.map(d => \`
              <div class="status pending">
                <div class="metric">\${d.metric}</div>
                <div class="action">\${d.actionType}</div>
                <div>\${d.rationale}</div>
                <button class="button success" onclick="approveDecision('\${d.signalId}')">✅ Одобрить</button>
                <button class="button danger" onclick="rejectDecision('\${d.signalId}')">❌ Отклонить</button>
              </div>
            \`).join('');
          document.getElementById('decisionsList').innerHTML = html;
        }
        
        function displayProposals(proposals) {
          const html = proposals.length === 0 ? 'Нет pending предложений' :
            proposals.map(p => \`
              <div class="status pending">
                <div><strong>\${p.extractedCase}</strong></div>
                <div>Confidence: \${(p.confidence * 100).toFixed(0)}%</div>
                <div>\${p.notes}</div>
                <button class="button success" onclick="acceptProposal('\${p.callDate}')">✅ Принять</button>
                <button class="button danger" onclick="rejectProposal('\${p.callDate}')">❌ Отклонить</button>
              </div>
            \`).join('');
          document.getElementById('proposalsList').innerHTML = html;
        }
        
        function approveDecision(signalId) {
          google.script.run
            .withSuccessHandler(() => {
              alert('Решение одобрено');
              refreshData();
            })
            .withFailureHandler(err => alert('Ошибка: ' + err.message))
            .approveDecision(signalId);
        }
        
        function rejectDecision(signalId) {
          google.script.run
            .withSuccessHandler(() => {
              alert('Решение отклонено');
              refreshData();
            })
            .withFailureHandler(err => alert('Ошибка: ' + err.message))
            .rejectDecision(signalId);
        }
        
        function acceptProposal(callDate) {
          google.script.run
            .withSuccessHandler(() => {
              alert('Предложение принято');
              refreshData();
            })
            .withFailureHandler(err => alert('Ошибка: ' + err.message))
            .acceptProposal(callDate);
        }
        
        function rejectProposal(callDate) {
          google.script.run
            .withSuccessHandler(() => {
              alert('Предложение отклонено');
              refreshData();
            })
            .withFailureHandler(err => alert('Ошибка: ' + err.message))
            .rejectProposal(callDate);
        }
        
        function clearHighlights() {
          google.script.run
            .withSuccessHandler(() => alert('Подсветки очищены'))
            .withFailureHandler(err => alert('Ошибка: ' + err.message))
            .clearAllHighlights();
        }
        
        // Загружаем данные при открытии
        refreshData();
      </script>
    </body>
    </html>
  `)
  .setTitle('AI Agent - Панель управления')
  .setWidth(400);
  
  SpreadsheetApp.getUi().showSidebar(html);
}

// ========== API ДЛЯ БОКОВОЙ ПАНЕЛИ ==========
function getPendingDecisions() {
  const ss = SpreadsheetApp.getActive();
  const decisionsSheet = ss.getSheetByName('Decisions');
  if (!decisionsSheet) return [];
  
  const values = decisionsSheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  
  return values
    .filter(row => row[idx.Status] === 'pending')
    .map(row => ({
      signalId: row[idx.SignalId],
      metric: row[idx.Rationale] ? row[idx.Rationale].split(';')[0] : '',
      actionType: row[idx.SuggestedActionType],
      rationale: row[idx.Rationale]
    }));
}

function getPendingProposals() {
  const ss = SpreadsheetApp.getActive();
  const proposalsSheet = ss.getSheetByName('Proposals');
  if (!proposalsSheet) return [];
  
  const values = proposalsSheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  
  return values
    .filter(row => row[idx.Status] === 'pending')
    .map(row => ({
      callDate: row[idx.CallDate],
      extractedCase: row[idx.ExtractedCase],
      confidence: row[idx.Confidence],
      notes: row[idx.Notes]
    }));
}

function approveDecision(signalId) {
  const ss = SpreadsheetApp.getActive();
  const decisionsSheet = ss.getSheetByName('Decisions');
  if (!decisionsSheet) return;
  
  const values = decisionsSheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  
  for (let i = 0; i < values.length; i++) {
    if (values[i][idx.SignalId] === signalId) {
      const row = i + 2; // +2 because we removed header
      decisionsSheet.getRange(row, idx.Status + 1).setValue('approved');
      decisionsSheet.getRange(row, idx.ApprovedBy + 1).setValue(Session.getActiveUser().getEmail());
      break;
    }
  }
}

function rejectDecision(signalId) {
  const ss = SpreadsheetApp.getActive();
  const decisionsSheet = ss.getSheetByName('Decisions');
  if (!decisionsSheet) return;
  
  const values = decisionsSheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  
  for (let i = 0; i < values.length; i++) {
    if (values[i][idx.SignalId] === signalId) {
      const row = i + 2;
      decisionsSheet.getRange(row, idx.Status + 1).setValue('rejected');
      decisionsSheet.getRange(row, idx.ApprovedBy + 1).setValue(Session.getActiveUser().getEmail());
      break;
    }
  }
}

function acceptProposal(callDate) {
  const ss = SpreadsheetApp.getActive();
  const proposalsSheet = ss.getSheetByName('Proposals');
  const algorithmSheet = ss.getSheetByName('Algorithm');
  if (!proposalsSheet || !algorithmSheet) return;
  
  const values = proposalsSheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  
  for (let i = 0; i < values.length; i++) {
    if (values[i][idx.CallDate] === callDate && values[i][idx.Status] === 'pending') {
      const row = i + 2;
      proposalsSheet.getRange(row, idx.Status + 1).setValue('accepted');
      
      // Добавляем новое правило в Algorithm
      const newRuleId = 'R' + String(Date.now()).slice(-6);
      const newRule = [
        newRuleId,
        'auto', // Block
        'Auto-generated', // Metric
        'custom', // ConditionType
        values[i][idx.SuggestedRuleDiff], // ConditionParams
        'custom_action', // ActionType
        values[i][idx.SuggestedRuleDiff], // ActionParams
        'medium', // Severity
        'N', // AutoApply
        'Y', // Active
        new Date().toISOString(), // CreatedAt
        `Из созвона ${callDate}: ${values[i][idx.ExtractedCase]}` // Notes
      ];
      
      algorithmSheet.appendRow(newRule);
      break;
    }
  }
}

function rejectProposal(callDate) {
  const ss = SpreadsheetApp.getActive();
  const proposalsSheet = ss.getSheetByName('Proposals');
  if (!proposalsSheet) return;
  
  const values = proposalsSheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  
  for (let i = 0; i < values.length; i++) {
    if (values[i][idx.CallDate] === callDate && values[i][idx.Status] === 'pending') {
      const row = i + 2;
      proposalsSheet.getRange(row, idx.Status + 1).setValue('rejected');
      break;
    }
  }
}

function clearAllHighlights() {
  const ss = SpreadsheetApp.getActive();
  const dataSheets = findDataSheets(); // ИСПРАВЛЕНО: используем findDataSheets()
  dataSheets.forEach(name => {
    const sheet = ss.getSheetByName(name);
    if (sheet) {
      sheet.clearFormat();
      sheet.clearNotes();
    }
  });
}

// ========== НАСТРОЙКА ТРИГГЕРОВ ==========
function setupTriggers() {
  // Удаляем старые триггеры
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'scanSignals') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Создаем новый триггер на каждый день в 9:00
  ScriptApp.newTrigger('scanSignals')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
  
  SpreadsheetApp.getUi().alert('✅ Триггер настроен: ежедневное сканирование в 9:00');
}

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
function ensureSheetWithHeader(ss, name, headers) {
  const sheet = ss.getSheetByName(name) || ss.insertSheet(name);
  const firstRow = sheet.getRange(1, 1, 1, headers.length).getValues()[0];
  const needHeaders = firstRow.some(v => !v);
  if (needHeaders) {
    sheet.clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
  }
}

function readAlgorithm(sheet) {
  if (!sheet) return [];
  const values = sheet.getDataRange().getValues();
  const headers = values.shift() || [];
  const idx = indexMap_(headers);
  return values
    .filter(row => String(row[idx.Active] || '').toUpperCase() === 'Y') // Фильтруем только активные правила
    .map(row => {
      const params = parseJsonSafe_(row[idx.ConditionParams]);
      return {
        RuleId: row[idx.RuleId] || '',
        Block: row[idx.Block] || '',
        Metric: row[idx.Metric] || '',
        ConditionType: (row[idx.ConditionType] || 'ratio').toLowerCase(),
        ConditionParams: params || {},
        ActionType: row[idx.ActionType] || '',
        ActionParamsRaw: row[idx.ActionParams] || '',
        Severity: row[idx.Severity] || 'medium'
      };
    });
}

function matchRule(rules, metricName, context) {
  const candidates = rules.filter(r => r.Metric === metricName);
  for (const r of candidates) {
    if (r.ConditionType === 'ratio') {
      const drop = Math.abs(context.deltaPct);
      const dropPct = numberOr_(r.ConditionParams.drop_pct, 0.15);
      const minSamples = numberOr_(r.ConditionParams.min_samples, CONFIG.minSamplesDefault);
      if (context.samples >= minSamples && context.deltaPct <= -dropPct) {
        return r;
      }
    }
  }
  return null;
}

function findLastDateColumn(sheet) {
  const row = sheet.getRange(CONFIG.headerRow, CONFIG.dateStartCol, 1, sheet.getLastColumn() - CONFIG.dateStartCol + 1).getValues()[0];
  let lastCol = null;
  for (let i = 0; i < row.length; i++) {
    const v = row[i];
    if (v) lastCol = CONFIG.dateStartCol + i;
  }
  return lastCol;
}

function rangeBack(startCol, count, minCol) {
  const cols = [];
  for (let c = startCol; c >= minCol && cols.length < count; c--) cols.push(c);
  return cols;
}

function toNumberSafe(v) {
  if (typeof v === 'number') return v;
  const s = String(v).replace('%','').replace(',','.');
  const n = parseFloat(s);
  return isFinite(n) ? n : NaN;
}

function avg(arr) {
  if (!arr.length) return NaN;
  return arr.reduce((a,b)=>a+b,0) / arr.length;
}

function computeDeltaPct(currentValue, baseline) {
  const denom = Math.abs(baseline) < 1e-9 ? 1e-9 : baseline;
  return (currentValue - baseline) / denom;
}

function indexMap_(headers) {
  const map = {};
  headers.forEach((h, i) => map[h] = i);
  return map;
}

function numberOr_(v, d) {
  const n = typeof v === 'number' ? v : parseFloat(v);
  return isFinite(n) ? n : d;
}

function parseJsonSafe_(raw) {
  try {
    if (!raw) return null;
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch(e) {
    return null;
  }
}

function appendRow_(sheet, row) {
  sheet.appendRow(row);
  const lastRow = sheet.getLastRow();
  const id = `${sheet.getName()}!R${lastRow}`;
  sheet.getRange(lastRow, 1).setNote(`id=${id}`);
  return id;
}

function highlightCellWithNote_(sheet, r, c, rule, note) {
  const bgColor = CONFIG.highlight[rule.Severity] || CONFIG.highlight.bg;
  sheet.getRange(r, c).setBackground(bgColor);
  const prev = sheet.getRange(r, c).getNote();
  sheet.getRange(r, c).setNote(prev ? (prev + '\n' + note) : note);
}

function makeA1NotationLink_(ss, sheet, r, c) {
  const url = ss.getUrl();
  const gid = sheet.getSheetId();
  const a1 = sheet.getRange(r, c).getA1Notation();
  return `${url}#gid=${gid}&range=${encodeURIComponent(a1)}`;
}

function formatDate_(d) {
  if (!d) return '';
  try {
    if (Object.prototype.toString.call(d) === '[object Date]') return Utilities.formatDate(d, Session.getScriptTimeZone(), 'yyyy-MM-dd');
    const parsed = new Date(d);
    return Utilities.formatDate(parsed, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  } catch(e) {
    return String(d);
  }
}

// ========== ГЕНЕРАЦИЯ САММАРИ ==========
function generateSummary() {
  const ss = SpreadsheetApp.getActive();
  
  try {
    // Получаем последние сигналы
    const signalsSheet = ss.getSheetByName('Signals');
    if (!signalsSheet) {
      SpreadsheetApp.getUi().alert('Ошибка', 'Лист "Сигналы" не найден', SpreadsheetApp.getUi().ButtonSet.OK);
      return;
    }
    
    const signalsData = signalsSheet.getDataRange().getValues();
    if (signalsData.length <= 1) {
      SpreadsheetApp.getUi().alert('Нет данных', 'Сигналы не найдены', SpreadsheetApp.getUi().ButtonSet.OK);
      return;
    }
    
    // Фильтруем сигналы за последние 24 часа
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    const recentSignals = signalsData.slice(1).filter(row => {
      const signalTime = new Date(row[0]);
      return signalTime >= yesterday;
    });
    
    if (recentSignals.length === 0) {
      SpreadsheetApp.getUi().alert('Нет новых сигналов', 'За последние 24 часа новых отклонений не найдено', SpreadsheetApp.getUi().ButtonSet.OK);
      return;
    }
    
    // Генерируем саммари
    let summary = 'САММАРИ ИЗМЕНЕНИЙ\n\n';
    summary += `Время анализа: ${now.toLocaleString('ru-RU')}\n`;
    summary += `Найдено отклонений: ${recentSignals.length}\n\n`;
    
    // Группируем по блокам
    const byBlock = {};
    recentSignals.forEach(signal => {
      const block = signal[1];
      if (!byBlock[block]) byBlock[block] = [];
      byBlock[block].push(signal);
    });
    
    // Добавляем детали по блокам с источниками
    Object.keys(byBlock).forEach(block => {
      summary += `${block.toUpperCase()}:\n`;
      byBlock[block].forEach(signal => {
        const metric = signal[2];
        const change = signal[6];
        const severity = signal[10];
        const link = signal[9]; // Ссылка на ячейку
        const emoji = severity === 'Высокая' ? '🔴' : severity === 'Средняя' ? '🟡' : '🟢';
        summary += `  ${emoji} ${metric}: ${change}% (${link})\n`;
      });
      summary += '\n';
    });
    
    // Добавляем источники данных
    summary += 'ИСТОЧНИКИ ДАННЫХ:\n';
    const uniqueSheets = [...new Set(recentSignals.map(s => s[9].split('!')[0]))];
    uniqueSheets.forEach(sheet => {
      summary += `- ${sheet}: ${recentSignals.filter(s => s[9].startsWith(sheet)).length} сигналов\n`;
    });
    summary += '\n';
    
    // Добавляем рекомендации
    summary += 'РЕКОМЕНДАЦИИ:\n';
    summary += '1. Проверьте лист "Сигналы" для деталей\n';
    summary += '2. Просмотрите предложения в листе "Решения"\n';
    summary += '3. Одобрите или отклоните предложения\n';
    summary += '4. Проверьте источники данных по ссылкам выше\n';
    
    // Показываем саммари
    SpreadsheetApp.getUi().alert('Саммари изменений', summary, SpreadsheetApp.getUi().ButtonSet.OK);
    
    // Записываем в лист "Изменения"
    const changesSheet = ss.getSheetByName('Изменения');
    if (changesSheet) {
      changesSheet.appendRow([
        now.toISOString(),
        'Генерация саммари',
        `Проанализировано ${recentSignals.length} сигналов`,
        'Успешно',
        'AI Агент',
        'Завершено'
      ]);
    }
    
  } catch (error) {
    console.error('Ошибка генерации саммари:', error);
    SpreadsheetApp.getUi().alert('Ошибка', 'Не удалось сгенерировать саммари: ' + error.message, SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

// ========== СОХРАНЯЕМ СТАРЫЙ СКРИПТ ==========
function znach2() {
  var spreadsheet = SpreadsheetApp.getActive();
  spreadsheet.getActiveRange().copyTo(spreadsheet.getActiveRange(), SpreadsheetApp.CopyPasteType.PASTE_VALUES, false);
}
