import 'dotenv/config';
import { google } from 'googleapis';
import { getGoogleAuth } from '../google/auth.js';

interface AlgorithmRule {
  ruleId: string;
  block: string;
  metric: string;
  conditionType: string;
  conditionParams: string;
  actionType: string;
  actionParams: string;
  severity: string;
  autoApply: string;
  active: string;
  notes: string;
}

const STARTER_RULES: AlgorithmRule[] = [
  {
    ruleId: 'R001',
    block: 'funnel',
    metric: 'Конверсия в корзину, %',
    conditionType: 'ratio',
    conditionParams: '{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}',
    actionType: 'price_adjust',
    actionParams: '{"competitor_scan":"on","target_delta_pct":"match_top3-1%","floor_margin_pct":12}',
    severity: 'high',
    autoApply: 'N',
    active: 'Y',
    notes: 'Автоматически добавлено через Node.js'
  },
  {
    ruleId: 'R002',
    block: 'ads',
    metric: 'CTR',
    conditionType: 'ratio',
    conditionParams: '{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}',
    actionType: 'content_ticket',
    actionParams: '{"task":"replace_main_image","priority":"high","assignee":"content_manager"}',
    severity: 'medium',
    autoApply: 'N',
    active: 'Y',
    notes: 'Автоматически добавлено через Node.js'
  },
  {
    ruleId: 'R003',
    block: 'funnel',
    metric: 'Переходы в карточку',
    conditionType: 'ratio',
    conditionParams: '{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}',
    actionType: 'ads_bid_adjust',
    actionParams: '{"target":"clicks","delta":"-10% to +10%","guard":"acos<=0.3"}',
    severity: 'medium',
    autoApply: 'N',
    active: 'Y',
    notes: 'Автоматически добавлено через Node.js'
  },
  {
    ruleId: 'R004',
    block: 'funnel',
    metric: 'Положили в корзину',
    conditionType: 'ratio',
    conditionParams: '{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}',
    actionType: 'price_adjust',
    actionParams: '{"competitor_scan":"on","target_delta_pct":"match_top3-2%","floor_margin_pct":10}',
    severity: 'high',
    autoApply: 'N',
    active: 'Y',
    notes: 'Автоматически добавлено через Node.js'
  },
  {
    ruleId: 'R005',
    block: 'funnel',
    metric: 'CR',
    conditionType: 'ratio',
    conditionParams: '{"baseline":"rolling_7d","drop_pct":0.1,"min_samples":5}',
    actionType: 'content_ticket',
    actionParams: '{"task":"review_product_description","priority":"high","assignee":"content_manager"}',
    severity: 'high',
    autoApply: 'N',
    active: 'Y',
    notes: 'Автоматически добавлено через Node.js'
  },
  {
    ruleId: 'R006',
    block: 'ads',
    metric: 'Показы',
    conditionType: 'ratio',
    conditionParams: '{"baseline":"rolling_7d","drop_pct":0.3,"min_samples":5}',
    actionType: 'ads_budget_adjust',
    actionParams: '{"target":"impressions","delta":"+20%","max_budget_increase":5000}',
    severity: 'low',
    autoApply: 'N',
    active: 'Y',
    notes: 'Автоматически добавлено через Node.js'
  }
];

async function setupAlgorithm() {
  const spreadsheetId = process.env.GOOGLE_SHEETS_ID || '';
  if (!spreadsheetId) throw new Error('Missing GOOGLE_SHEETS_ID');

  const auth = getGoogleAuth();
  const sheets = google.sheets({ version: 'v4', auth });

  try {
    // Проверяем, существует ли лист Algorithm
    const spreadsheet = await sheets.spreadsheets.get({ spreadsheetId });
    const algorithmSheet = spreadsheet.data.sheets?.find(sheet => 
      sheet.properties?.title === 'Algorithm'
    );

    if (!algorithmSheet) {
      console.log('Создаем лист Algorithm...');
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId,
        requestBody: {
          requests: [{
            addSheet: {
              properties: {
                title: 'Algorithm',
                gridProperties: { rowCount: 1000, columnCount: 12 }
              }
            }
          }]
        }
      });
    }

    // Устанавливаем заголовки
    const headers = [
      'RuleId', 'Block', 'Metric', 'ConditionType', 'ConditionParams', 
      'ActionType', 'ActionParams', 'Severity', 'AutoApply', 'Active', 
      'CreatedAt', 'Notes'
    ];

    await sheets.spreadsheets.values.update({
      spreadsheetId,
      range: 'Algorithm!A1:L1',
      valueInputOption: 'RAW',
      requestBody: { values: [headers] }
    });

    // Проверяем, есть ли уже данные
    const existingData = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: 'Algorithm!A2:L1000'
    });

    const hasExistingData = existingData.data.values && existingData.data.values.length > 0;

    if (hasExistingData) {
      console.log('В листе Algorithm уже есть данные. Пропускаем добавление стартовых правил.');
      return;
    }

    // Добавляем стартовые правила
    const rows = STARTER_RULES.map(rule => [
      rule.ruleId,
      rule.block,
      rule.metric,
      rule.conditionType,
      rule.conditionParams,
      rule.actionType,
      rule.actionParams,
      rule.severity,
      rule.autoApply,
      rule.active,
      new Date().toISOString(),
      rule.notes
    ]);

    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: 'Algorithm!A:L',
      valueInputOption: 'USER_ENTERED',
      requestBody: { values: rows }
    });

    console.log(`✅ Добавлено ${STARTER_RULES.length} стартовых правил в лист Algorithm`);

  } catch (error) {
    console.error('Ошибка при настройке Algorithm:', error);
    throw error;
  }
}

async function main() {
  try {
    await setupAlgorithm();
    console.log('🎉 Настройка Algorithm завершена успешно!');
  } catch (error) {
    console.error('❌ Ошибка:', error);
    process.exit(1);
  }
}

main();
