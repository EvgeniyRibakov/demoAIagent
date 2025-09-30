# Action Plan for AI Agent

## ✅ COMPLETED
- Google Sheets API configured
- Sheets created: Algorithm, Signals, Decisions, Proposals
- 6 starter rules added
- Google Drive API working
- Configuration set up

## 🎯 NEXT STEPS

### 1. Google Apps Script (5 min)
- Open [spreadsheet](https://docs.google.com/spreadsheets/d/18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ/edit)
- Extensions → Apps Script
- Copy code from `src/apps-script/enhanced-agent.gs`
- Save → "🤖 AI Agent" menu appears

### 2. Fix OpenAI API (10 min)
**Problem:** Avast blocks access
**Solution:**
- Avast → Settings → Exceptions
- Add: `python.exe`, project folder, `poetry.exe`
- Or temporarily disable real-time protection

### 3. Configure .env (5 min)
```env
GOOGLE_APPLICATION_CREDENTIALS=./ai-agent-sheets-473515-12c6cb0e6fab.json
GOOGLE_SHEETS_ID=18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ
GOOGLE_DRIVE_CALLS_FOLDER_ID=your_folder_id
OPENAI_API_KEY=sk-your-key-here
```

### 4. Testing (10 min)
```bash
# Test connections
poetry run python src/ai_agent/setup/test_connections.py

# Test scanning (in Google Sheets)
# Menu "🤖 AI Agent" → "📊 Scan Signals"
```

## 📊 Status
| Component | Status |
|-----------|--------|
| Google Sheets | ✅ |
| Google Drive | ✅ |
| Apps Script | ⏳ |
| OpenAI API | ❌ |
| Configuration | ✅ |

## 🚀 After OpenAI fix
1. Test call analysis: `poetry run python src/ai_agent/jobs/proposals_from_drive.py`
2. Setup tl;dv → Google Drive
3. Automate triggers

**Main issue:** Avast antivirus blocks OpenAI API


