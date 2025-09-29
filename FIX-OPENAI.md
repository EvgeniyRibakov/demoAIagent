# Fix OpenAI API Issue

## Problem
```
ERROR: Ошибка настройки OpenAI: [Errno 13] Permission denied: '\\\\.\\aswMonFltProxy\\FFFFAE8C4D6F39D0'
```

## Cause
Avast antivirus blocks OpenAI API access through `aswMonFltProxy` filter.

## Solutions

### Option 1: Add Avast Exceptions (Recommended)
1. Open Avast Antivirus
2. Go to Settings → Exceptions
3. Add exceptions for:
   - `C:\Users\fisher\AppData\Local\Programs\Python\Python312\python.exe`
   - `C:\Users\fisher\PycharmProjects\AI-agent_with_Cursor\`
   - `C:\Users\fisher\AppData\Local\Programs\Python\Python312\Scripts\poetry.exe`

### Option 2: Temporarily Disable Protection
1. Open Avast
2. Go to Settings → General
3. Temporarily disable "Real-time Protection"
4. Run test
5. Re-enable protection

### Option 3: Use Different Antivirus
- Temporarily disable Avast
- Use Windows Defender
- Or install different antivirus

## Verification
```bash
poetry run python src/ai_agent/setup/test_connections.py
```

Should show:
```
OpenAI API           SUCCESS: ПРОЙДЕН
```
