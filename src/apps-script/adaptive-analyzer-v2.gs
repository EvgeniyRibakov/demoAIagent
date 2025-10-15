// ========== АДАПТИВНЫЙ АНАЛИЗАТОР V2.0 ==========
// Умный анализатор который сам определяет структуру таблицы
// Работает даже если переименовали или переместили колонки

// ========== ГЛАВНОЕ МЕНЮ ==========
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 AI Агент v2.0')
    .addItem('▶️ ЗАПУСТИТЬ АНАЛИЗ', 'runSmartAnalysis')
    .addSeparator()
    .addItem('⚙️ Настройки', 'showSettings')
    .addItem('📊 История анализов', 'showHistory')
    .addItem('❓ Помощь', 'showHelp')
    .addToUi();
}

// ========== УМНОЕ ОПРЕДЕЛЕНИЕ СТРУКТУРЫ ==========

/**
 * Находит колонку по ключевым словам (не зависит от позиции)
 */
function findColumn(sheet, keywords, startCol = 1) {
  const lastCol = sheet.getLastColumn();
  const headers = sheet.getRange(1, startCol, 1, lastCol - startCol + 1).getValues()[0];
  
  for (let i = 0; i < headers.length; i++) {
    const header = String(headers[i]).toLowerCase().trim();
    
    if (!header) continue;
    
    // Проверяем совпадение с любым из ключевых слов
    for (const keyword of keywords) {
      if (header.includes(keyword.toLowerCase())) {
        return startCol + i; // Возвращаем номер колонки
      }
    }
  }
  
  return null; // Не найдено
}

/**
 * Находит все колонки с датами
 */
function findDateColumns(sheet) {
  const lastCol = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  
  const dateColumns = [];
  const datePattern = /\d{1,2}\.\d{1,2}\.(\d{2}|\d{4})/; // DD.MM.YY или DD.MM.YYYY
  
  for (let i = 0; i < headers.length; i++) {
    const header = String(headers[i]).trim();
    
    if (datePattern.test(header)) {
      // Парсим дату
      const match = header.match(datePattern);
      const dateStr = match[0];
      
      dateColumns.push({
        col: i + 1,
        dateStr: dateStr,
        header: header
      });
    }
  }
  
  return dateColumns;
}

/**
 * Находит две последние даты (сегодня и вчера)
 */
function findLastTwoDates(dateColumns) {
  if (dateColumns.length < 2) {
    return null;
  }
  
  // Парсим даты
  const parsed = dateColumns.map(dc => {
    const parts = dc.dateStr.split('.');
    let day = parseInt(parts[0], 10);
    let month = parseInt(parts[1], 10) - 1; // Месяцы с 0
    let year = parseInt(parts[2], 10);
    
    // Если год двузначный, добавляем 2000
    if (year < 100) {
      year += 2000;
    }
    
    const date = new Date(year, month, day);
    
    return {
      ...dc,
      date: date
    };
  });
  
  // Сортируем по дате
  parsed.sort((a, b) => a.date - b.date);
  
  // Берем две последние
  const today = parsed[parsed.length - 1];
  const yesterday = parsed[parsed.length - 2];
  
  return {
    today: today,
    yesterday: yesterday
  };
}

/**
 * Определяет тип данных в колонке
 */
function detectColumnType(sheet, colIndex, startRow = 2, sampleSize = 10) {
  const lastRow = Math.min(sheet.getLastRow(), startRow + sampleSize - 1);
  
  if (lastRow < startRow) return 'empty';
  
  const values = sheet.getRange(startRow, colIndex, lastRow - startRow + 1, 1).getValues();
  
  let hasPercent = 0;
  let hasNumbers = 0;
  let hasDates = 0;
  let hasText = 0;
  
  for (const [value] of values) {
    if (!value || value === '') continue;
    
    const str = String(value).trim();
    
    if (str.includes('%')) hasPercent++;
    else if (!isNaN(parseFloat(str.replace(/[\s\xa0,]/g, '')))) hasNumbers++;
    else if (str.match(/\d{1,2}\.\d{1,2}\.(\d{2}|\d{4})/)) hasDates++;
    else hasText++;
  }
  
  // Определяем преобладающий тип
  const max = Math.max(hasPercent, hasNumbers, hasDates, hasText);
  
  if (max === 0) return 'empty';
  if (max === hasDates) return 'date';
  if (max === hasPercent) return 'percentage';
  if (max === hasNumbers) return 'number';
  
  return 'text';
}

/**
 * Находит строку где начинаются данные (после заголовков)
 */
function findDataStartRow(sheet) {
  // Обычно данные начинаются со 2-й или 3-й строки
  // Проверяем первые 5 строк
  
  for (let row = 2; row <= 5; row++) {
    const firstCell = sheet.getRange(row, 1).getValue();
    
    if (firstCell && String(firstCell).trim() !== '') {
      // Проверяем что это не заголовок (не содержит слова типа "метрика", "название" и т.д.)
      const str = String(firstCell).toLowerCase();
      
      if (!str.includes('метрика') && !str.includes('название') && 
          !str.includes('показатель') && !str.includes('параметр')) {
        return row;
      }
    }
  }
  
  return 2; // По умолчанию
}

/**
 * Автоматически определяет структуру листа
 */
function detectSheetStructure(sheet) {
  Logger.log('Определяем структуру листа: ' + sheet.getName());
  
  const structure = {
    sheetName: sheet.getName(),
    dateColumns: findDateColumns(sheet),
    dataStartRow: findDataStartRow(sheet),
    columns: {}
  };
  
  // Находим колонку с названиями метрик
  const metricCol = findColumn(sheet, ['метрика', 'название', 'показатель', 'параметр'], 1);
  if (metricCol) {
    structure.columns.metric = metricCol;
  } else {
    // По умолчанию первая колонка
    structure.columns.metric = 1;
  }
  
  // Находим последние две даты
  if (structure.dateColumns.length >= 2) {
    const dates = findLastTwoDates(structure.dateColumns);
    
    if (dates) {
      structure.todayCol = dates.today.col;
      structure.yesterdayCol = dates.yesterday.col;
      structure.todayDate = dates.today.dateStr;
      structure.yesterdayDate = dates.yesterday.dateStr;
    }
  }
  
  Logger.log('Структура определена: ' + JSON.stringify(structure));
  
  return structure;
}

// ========== ГИБКОЕ СОПОСТАВЛЕНИЕ С АЛГОРИТМАМИ ==========

/**
 * Находит правило для метрики (гибкое сопоставление)
 */
function matchMetricToRule(metricName, rules) {
  const metricLower = metricName.toLowerCase().trim();
  
  // 1. Точное совпадение
  for (const rule of rules) {
    if (rule.Metric.toLowerCase().trim() === metricLower) {
      return rule;
    }
  }
  
  // 2. Частичное совпадение по ключевым словам
  const metricKeywords = metricLower.split(/[\s,\-()]+/).filter(w => w.length > 2);
  
  for (const rule of rules) {
    const ruleKeywords = rule.Metric.toLowerCase().split(/[\s,\-()]+/).filter(w => w.length > 2);
    
    // Проверяем пересечение ключевых слов
    for (const mk of metricKeywords) {
      for (const rk of ruleKeywords) {
        if (mk === rk || mk.includes(rk) || rk.includes(mk)) {
          return rule;
        }
      }
    }
  }
  
  // 3. Сопоставление по синонимам
  const synonyms = {
    'ctr': ['кликабельность', 'click-through', 'переходы/показы'],
    'cr': ['конверсия', 'conversion rate'],
    'показы': ['impressions', 'views', 'просмотры'],
    'клики': ['clicks', 'переходы'],
    'корзина': ['cart', 'basket', 'добавления']
  };
  
  for (const [key, syns] of Object.entries(synonyms)) {
    const hasKeyInMetric = metricLower.includes(key) || syns.some(s => metricLower.includes(s));
    
    if (hasKeyInMetric) {
      // Ищем правило с таким же ключом или синонимом
      for (const rule of rules) {
        const ruleLower = rule.Metric.toLowerCase();
        if (ruleLower.includes(key) || syns.some(s => ruleLower.includes(s))) {
          return rule;
        }
      }
    }
  }
  
  return null; // Правило не найдено
}

/**
 * Загружает правила из листа "Алгоритм"
 */
function loadRules() {
  const ss = SpreadsheetApp.getActive();
  const algorithmSheet = ss.getSheetByName('Algorithm') || ss.getSheetByName('Алгоритм');
  
  if (!algorithmSheet) {
    Logger.log('Лист "Algorithm" не найден');
    return [];
  }
  
  const data = algorithmSheet.getDataRange().getValues();
  if (data.length <= 1) {
    Logger.log('Нет правил в листе "Algorithm"');
    return [];
  }
  
  const headers = data[0];
  const rules = [];
  
  // Определяем индексы колонок
  const colMap = {};
  headers.forEach((h, i) => {
    colMap[h] = i;
  });
  
  // Парсим правила
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    
    // Проверяем активность
    const active = String(row[colMap.Active] || '').toUpperCase() === 'Y';
    if (!active) continue;
    
    // Парсим параметры условия
    let conditionParams = {};
    try {
      const paramsStr = row[colMap.ConditionParams];
      if (paramsStr) {
        conditionParams = JSON.parse(paramsStr);
      }
    } catch (e) {
      Logger.log('Ошибка парсинга параметров правила: ' + e);
    }
    
    const rule = {
      RuleId: row[colMap.RuleId] || '',
      Block: row[colMap.Block] || '',
      Metric: row[colMap.Metric] || '',
      ConditionType: row[colMap.ConditionType] || 'ratio',
      ConditionParams: conditionParams,
      ActionType: row[colMap.ActionType] || '',
      ActionParams: row[colMap.ActionParams] || '',
      Severity: row[colMap.Severity] || 'medium',
      dropPct: conditionParams.drop_pct || 0.15,
      minSamples: conditionParams.min_samples || 5
    };
    
    rules.push(rule);
  }
  
  Logger.log('Загружено правил: ' + rules.length);
  return rules;
}

// ========== ГЛАВНАЯ ФУНКЦИЯ АНАЛИЗА ==========

/**
 * Запускает умный анализ
 */
function runSmartAnalysis() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActive();
  
  try {
    // Показываем прогресс
    ui.alert('Запуск анализа', 'Определяем структуру таблицы...', ui.ButtonSet.OK);
    
    // Загружаем правила
    const rules = loadRules();
    if (rules.length === 0) {
      ui.alert('Ошибка', 'Не найдены активные правила в листе "Algorithm"', ui.ButtonSet.OK);
      return;
    }
    
    // Находим листы с данными (автоматически)
    const dataSheetPattern = /^(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)\s+\d{4}$/i;
    const sheets = ss.getSheets();
    const dataSheets = sheets.filter(s => dataSheetPattern.test(s.getName()));
    
    if (dataSheets.length === 0) {
      ui.alert('Ошибка', 'Не найдены листы с данными (формат: "Месяц Год")', ui.ButtonSet.OK);
      return;
    }
    
    // Анализируем последний лист
    const sheet = dataSheets[dataSheets.length - 1];
    const structure = detectSheetStructure(sheet);
    
    if (!structure.todayCol || !structure.yesterdayCol) {
      ui.alert('Ошибка', 'Не найдены колонки с датами для сравнения', ui.ButtonSet.OK);
      return;
    }
    
    // Анализируем данные
    const anomalies = [];
    const lastRow = sheet.getLastRow();
    
    for (let row = structure.dataStartRow; row <= lastRow; row++) {
      const metricName = sheet.getRange(row, structure.columns.metric).getDisplayValue().trim();
      
      if (!metricName) continue;
      
      // Получаем значения
      const todayValue = parseNumber(sheet.getRange(row, structure.todayCol).getValue());
      const yesterdayValue = parseNumber(sheet.getRange(row, structure.yesterdayCol).getValue());
      
      if (todayValue === null || yesterdayValue === null) continue;
      if (todayValue === 0 && yesterdayValue === 0) continue;
      
      // Вычисляем изменение
      const changePct = yesterdayValue === 0 ? 100 : 
        ((todayValue - yesterdayValue) / Math.abs(yesterdayValue)) * 100;
      
      // Ищем подходящее правило
      const rule = matchMetricToRule(metricName, rules);
      
      if (rule) {
        // Проверяем условие
        const threshold = rule.dropPct * 100; // Переводим в проценты
        
        if (Math.abs(changePct) >= threshold && changePct < 0) { // Только падения
          anomalies.push({
            row: row,
            metric: metricName,
            yesterdayValue: yesterdayValue,
            todayValue: todayValue,
            changePct: changePct,
            rule: rule,
            severity: rule.Severity
          });
        }
      }
    }
    
    // Показываем результаты
    if (anomalies.length === 0) {
      ui.alert('Анализ завершен', 'Отклонений не найдено. Все показатели в норме! ✅', ui.ButtonSet.OK);
    } else {
      showResults(anomalies, structure);
    }
    
  } catch (e) {
    Logger.log('Ошибка анализа: ' + e);
    ui.alert('Ошибка', 'Произошла ошибка при анализе: ' + e.message, ui.ButtonSet.OK);
  }
}

/**
 * Показывает результаты анализа
 */
function showResults(anomalies, structure) {
  const ui = SpreadsheetApp.getUi();
  
  // Группируем по критичности
  const critical = anomalies.filter(a => a.severity === 'high');
  const important = anomalies.filter(a => a.severity === 'medium');
  const normal = anomalies.filter(a => a.severity === 'low');
  
  let message = `📊 АНАЛИЗ ЗАВЕРШЕН\n\n`;
  message += `Лист: ${structure.sheetName}\n`;
  message += `Сравнение: ${structure.yesterdayDate} vs ${structure.todayDate}\n\n`;
  message += `Найдено проблем: ${anomalies.length}\n`;
  message += `• Критичных: ${critical.length}\n`;
  message += `• Важных: ${important.length}\n`;
  message += `• Обычных: ${normal.length}\n\n`;
  
  if (critical.length > 0) {
    message += `🔴 СРОЧНО (требуют действий сегодня):\n\n`;
    critical.forEach(a => {
      message += `• ${a.metric}\n`;
      message += `  Изменение: ${a.changePct.toFixed(1)}%\n`;
      message += `  Действие: ${a.rule.ActionType}\n\n`;
    });
  }
  
  if (important.length > 0) {
    message += `🟡 ВАЖНО (требуют внимания):\n\n`;
    important.slice(0, 3).forEach(a => { // Первые 3
      message += `• ${a.metric}: ${a.changePct.toFixed(1)}%\n`;
    });
    
    if (important.length > 3) {
      message += `... и еще ${important.length - 3}\n`;
    }
  }
  
  message += `\n[Детали в листе "Сигналы"]`;
  
  ui.alert('Результаты анализа', message, ui.ButtonSet.OK);
}

/**
 * Парсит число из значения ячейки
 */
function parseNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  
  if (typeof value === 'number') return value;
  
  const str = String(value).replace(/[\s\xa0]/g, '').replace(',', '.').replace('%', '');
  const num = parseFloat(str);
  
  return isNaN(num) ? null : num;
}

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

function showSettings() {
  SpreadsheetApp.getUi().alert('Настройки', 'Раздел в разработке', SpreadsheetApp.getUi().ButtonSet.OK);
}

function showHistory() {
  SpreadsheetApp.getUi().alert('История', 'Раздел в разработке', SpreadsheetApp.getUi().ButtonSet.OK);
}

function showHelp() {
  const message = `🤖 AI АГЕНТ V2.0 - ПОМОЩЬ\n\n` +
    `Как использовать:\n\n` +
    `1. Нажмите "ЗАПУСТИТЬ АНАЛИЗ"\n` +
    `2. Агент автоматически:\n` +
    `   • Найдет листы с данными\n` +
    `   • Определит структуру\n` +
    `   • Сравнит вчера/сегодня\n` +
    `   • Применит правила\n` +
    `   • Выдаст рекомендации\n\n` +
    `3. Следуйте рекомендациям\n\n` +
    `Агент адаптируется если вы:\n` +
    `• Переименуете колонки\n` +
    `• Измените порядок\n` +
    `• Добавите новые метрики\n\n` +
    `Главное: храните правила в листе "Algorithm"!`;
  
  SpreadsheetApp.getUi().alert('Помощь', message, SpreadsheetApp.getUi().ButtonSet.OK);
}

