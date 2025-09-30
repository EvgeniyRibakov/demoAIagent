import OpenAI from 'openai';

const PROMPT = `Ты аналитик. Вход: транскрипт созвона и таблица правил (поля: Block, Metric, ConditionType, ConditionParams, ActionType, ActionParams). Задача:
1) Определи кейсы, где выполнены текущие правила (по смыслу).
2) Отдельно собери кейсы, где решение новое.
3) Для новых предложи минимальный diff для добавления в правила (ConditionType/Params, ActionType/Params), с кратким обоснованием и confidence 0..1.
Верни JSON со списками "by_rule" и "new".`;

export interface ProposalRow {
  callDate: string;
  extractedCase: string;
  existingRuleMatched: 'Y' | 'N';
  suggestedRuleDiff: string;
  confidence: number;
  status: 'pending';
  notes: string;
}

export async function extractProposalsFromTranscript(transcript: string, algorithmPreview?: string): Promise<ProposalRow[]> {
  const apiKey = process.env.OPENAI_API_KEY || '';
  if (!apiKey) throw new Error('Missing OPENAI_API_KEY');
  const client = new OpenAI({ apiKey });
  const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';

  const messages = [
    { role: 'system' as const, content: PROMPT },
    { role: 'user' as const, content: `АЛГОРИТМ (суммарно):\n${algorithmPreview || '(нет превью)'}\n\nТРАНСКРИПТ:\n${transcript}` }
  ];
  const res = await client.chat.completions.create({ model, messages, response_format: { type: 'json_object' } as any });
  const text = res.choices[0]?.message?.content || '{}';
  const json = JSON.parse(text);
  const rows: ProposalRow[] = [];
  const now = new Date().toISOString().slice(0, 10);
  const push = (it: any, matched: boolean) => rows.push({
    callDate: now,
    extractedCase: it.summary || it.case || '',
    existingRuleMatched: matched ? 'Y' : 'N',
    suggestedRuleDiff: JSON.stringify(it.diff || it.rule || {}, null, 2),
    confidence: Number(it.confidence ?? 0.5),
    status: 'pending',
    notes: it.rationale || ''
  });

  (json.by_rule || []).forEach((it: any) => push(it, true));
  (json.new || []).forEach((it: any) => push(it, false));
  return rows;
}

