import 'dotenv/config';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';

interface GoogleCredentials {
  type: string;
  project_id: string;
  private_key_id: string;
  private_key: string;
  client_email: string;
  client_id: string;
  auth_uri: string;
  token_uri: string;
  auth_provider_x509_cert_url: string;
  client_x509_cert_url: string;
}

async function createServiceAccount() {
  console.log('🔧 Настройка Google Service Account...');
  
  // Проверяем, есть ли уже credentials
  if (process.env.GOOGLE_CLIENT_EMAIL && process.env.GOOGLE_PRIVATE_KEY) {
    console.log('✅ Google credentials уже настроены в .env');
    return;
  }
  
  console.log(`
📋 Для настройки Google API выполните следующие шаги:

1. Откройте Google Cloud Console: https://console.cloud.google.com/
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API и Google Drive API:
   - APIs & Services → Library
   - Найдите "Google Sheets API" → Enable
   - Найдите "Google Drive API" → Enable
4. Создайте Service Account:
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Название: "ai-agent-sheets"
   - Role: "Editor" (или создайте кастомную роль)
5. Создайте ключ:
   - Нажмите на созданный Service Account
   - Keys → Add Key → Create new key → JSON
   - Скачайте JSON файл

6. Скопируйте данные из JSON в .env:
   - client_email → GOOGLE_CLIENT_EMAIL
   - private_key → GOOGLE_PRIVATE_KEY (в кавычках, с \\n)
   - project_id → GOOGLE_PROJECT_ID

7. Дайте доступ Service Account к вашей таблице:
   - Откройте Google Таблицу
   - Share → Добавьте email из client_email
   - Права: Editor

Пример .env:
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_CLIENT_EMAIL=ai-agent-sheets@your-project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
GOOGLE_SHEETS_ID=your-spreadsheet-id
GOOGLE_DRIVE_CALLS_FOLDER_ID=your-folder-id
OPENAI_API_KEY=sk-...
`);
}

async function setupSheetsSchema() {
  const spreadsheetId = process.env.GOOGLE_SHEETS_ID;
  if (!spreadsheetId) {
    console.log('❌ GOOGLE_SHEETS_ID не найден в .env');
    return false;
  }

  try {
    const auth = new google.auth.JWT({
      email: process.env.GOOGLE_CLIENT_EMAIL,
      key: (process.env.GOOGLE_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
      scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
      ]
    });

    const sheets = google.sheets({ version: 'v4', auth });
    const drive = google.drive({ version: 'v3', auth });

    console.log('🔍 Проверяем доступ к таблице...');
    
    // Проверяем доступ к таблице
    const spreadsheet = await sheets.spreadsheets.get({ spreadsheetId });
    console.log(`✅ Доступ к таблице: "${spreadsheet.data.properties?.title}"`);

    // Создаем листы если их нет
    const existingSheets = spreadsheet.data.sheets?.map(s => s.properties?.title) || [];
    const requiredSheets = ['Algorithm', 'Signals', 'Decisions', 'Proposals'];
    
    const sheetsToCreate = requiredSheets.filter(name => !existingSheets.includes(name));
    
    if (sheetsToCreate.length > 0) {
      console.log(`📝 Создаем листы: ${sheetsToCreate.join(', ')}`);
      
      const requests = sheetsToCreate.map(title => ({
        addSheet: {
          properties: {
            title,
            gridProperties: { rowCount: 1000, columnCount: 20 }
          }
        }
      }));

      await sheets.spreadsheets.batchUpdate({
        spreadsheetId,
        requestBody: { requests }
      });
    }

    // Устанавливаем заголовки
    const headers = {
      Algorithm: ['RuleId', 'Block', 'Metric', 'ConditionType', 'ConditionParams', 'ActionType', 'ActionParams', 'Severity', 'AutoApply', 'Active', 'CreatedAt', 'Notes'],
      Signals: ['Timestamp', 'Block', 'Metric', 'Date', 'CurrentValue', 'BaselineValue', 'DeltaPct', 'RuleId', 'Status', 'LinkToCell', 'Severity'],
      Decisions: ['SignalId', 'SuggestedActionType', 'ActionParams', 'Rationale', 'Status', 'ApprovedBy', 'AppliedAt', 'AuditLog', 'Confidence'],
      Proposals: ['CallDate', 'ExtractedCase', 'ExistingRuleMatched', 'SuggestedRuleDiff', 'Confidence', 'Status', 'Notes', 'RuleId']
    };

    for (const [sheetName, headerRow] of Object.entries(headers)) {
      await sheets.spreadsheets.values.update({
        spreadsheetId,
        range: `${sheetName}!A1:${String.fromCharCode(65 + headerRow.length - 1)}1`,
        valueInputOption: 'RAW',
        requestBody: { values: [headerRow] }
      });
      console.log(`✅ Заголовки установлены для листа: ${sheetName}`);
    }

    // Добавляем стартовые правила в Algorithm
    const starterRules = [
      ['R001', 'funnel', 'Конверсия в корзину, %', 'ratio', '{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}', 'price_adjust', '{"competitor_scan":"on","target_delta_pct":"match_top3-1%","floor_margin_pct":12}', 'high', 'N', 'Y', new Date().toISOString(), 'Автоматически добавлено'],
      ['R002', 'ads', 'CTR', 'ratio', '{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}', 'content_ticket', '{"task":"replace_main_image","priority":"high","assignee":"content_manager"}', 'medium', 'N', 'Y', new Date().toISOString(), 'Автоматически добавлено'],
      ['R003', 'funnel', 'Переходы в карточку', 'ratio', '{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}', 'ads_bid_adjust', '{"target":"clicks","delta":"-10% to +10%","guard":"acos<=0.3"}', 'medium', 'N', 'Y', new Date().toISOString(), 'Автоматически добавлено'],
      ['R004', 'funnel', 'Положили в корзину', 'ratio', '{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}', 'price_adjust', '{"competitor_scan":"on","target_delta_pct":"match_top3-2%","floor_margin_pct":10}', 'high', 'N', 'Y', new Date().toISOString(), 'Автоматически добавлено'],
      ['R005', 'funnel', 'CR', 'ratio', '{"baseline":"rolling_7d","drop_pct":0.1,"min_samples":5}', 'content_ticket', '{"task":"review_product_description","priority":"high","assignee":"content_manager"}', 'high', 'N', 'Y', new Date().toISOString(), 'Автоматически добавлено'],
      ['R006', 'ads', 'Показы', 'ratio', '{"baseline":"rolling_7d","drop_pct":0.3,"min_samples":5}', 'ads_budget_adjust', '{"target":"impressions","delta":"+20%","max_budget_increase":5000}', 'low', 'N', 'Y', new Date().toISOString(), 'Автоматически добавлено']
    ];

    // Проверяем, есть ли уже правила
    const existingData = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: 'Algorithm!A2:L1000'
    });

    if (!existingData.data.values || existingData.data.values.length === 0) {
      await sheets.spreadsheets.values.append({
        spreadsheetId,
        range: 'Algorithm!A:L',
        valueInputOption: 'USER_ENTERED',
        requestBody: { values: starterRules }
      });
      console.log(`✅ Добавлено ${starterRules.length} стартовых правил в Algorithm`);
    } else {
      console.log('ℹ️ В Algorithm уже есть данные, пропускаем добавление правил');
    }

    return true;

  } catch (error: any) {
    console.error('❌ Ошибка при настройке Google Sheets:', error.message);
    if (error.message.includes('PERMISSION_DENIED')) {
      console.log(`
🔐 Проблема с правами доступа:

1. Убедитесь, что Service Account добавлен в таблицу:
   - Откройте Google Таблицу
   - Share → Добавьте email: ${process.env.GOOGLE_CLIENT_EMAIL}
   - Права: Editor

2. Проверьте GOOGLE_SHEETS_ID в .env:
   - Скопируйте ID из URL таблицы
   - URL: https://docs.google.com/spreadsheets/d/[SHEETS_ID]/edit
`);
    }
    return false;
  }
}

async function setupAppsScript() {
  console.log(`
📝 Для завершения настройки добавьте Apps Script в таблицу:

1. Откройте вашу Google Таблицу
2. Extensions → Apps Script
3. Удалите весь существующий код
4. Скопируйте код из файла: src/apps-script/enhanced-agent.gs
5. Сохраните (Ctrl+S)
6. Вернитесь в таблицу
7. Обновите страницу (F5)
8. Появится меню "🤖 AI Agent"

Тестирование:
- 🤖 AI Agent → 🔧 Настройка схемы
- 🤖 AI Agent → 📊 Сканировать сигналы
- 🤖 AI Agent → 📋 Панель управления
`);
}

async function main() {
  console.log('🚀 Настройка AI Agent для Google Sheets...\n');
  
  // Проверяем .env
  if (!fs.existsSync('.env')) {
    console.log('❌ Файл .env не найден. Скопируйте .env.example в .env и заполните переменные.');
    return;
  }

  // Настраиваем Service Account
  await createServiceAccount();
  
  // Настраиваем схему таблицы
  const success = await setupSheetsSchema();
  
  if (success) {
    console.log('\n✅ Google Sheets настроены успешно!');
    await setupAppsScript();
    
    console.log(`
🎉 MVP готов к использованию!

Следующие шаги:
1. Добавьте Apps Script в таблицу (инструкция выше)
2. Протестируйте сканирование сигналов
3. Настройте tl;dv → Google Drive для Этапа 2
4. Запустите: npm run proposals:from-drive

Ссылка на вашу таблицу:
https://docs.google.com/spreadsheets/d/${process.env.GOOGLE_SHEETS_ID}/edit
`);
  } else {
    console.log('\n❌ Настройка не завершена. Проверьте ошибки выше.');
  }
}

main().catch(console.error);
