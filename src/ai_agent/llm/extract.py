"""
LLM извлечение решений из транскриптов
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import openai
from ai_agent.config import config


@dataclass
class Proposal:
    """Предложение из транскрипта"""
    call_date: str
    extracted_case: str
    existing_rule_matched: bool
    suggested_rule_diff: str
    confidence: float
    status: str = "pending"
    notes: str = ""
    rule_id: str = ""


class LLMExtractor:
    """Класс для извлечения решений через LLM"""
    
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Настраивает клиент OpenAI"""
        if not config.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY не настроен")
            return
        
        try:
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            print("✅ OpenAI клиент настроен")
        except Exception as e:
            print(f"❌ Ошибка настройки OpenAI: {e}")
    
    def _get_prompt(self, transcript: str, algorithm_preview: str = None) -> str:
        """Формирует промпт для LLM"""
        
        system_prompt = """Ты аналитик маркетплейсов. Анализируешь транскрипты созвонов менеджеров для извлечения решений по отклонениям в метриках.

Задача:
1) Найди кейсы, где решения соответствуют существующим правилам алгоритма
2) Отдельно найди кейсы с новыми решениями, которых нет в алгоритме
3) Для новых решений предложи правило в формате JSON

Существующие правила (примеры):
- Конверсия упала → проверить цены конкурентов → скорректировать цену
- CTR упал → заменить главную картинку товара
- Показы упали → увеличить рекламный бюджет
- Переходы упали → скорректировать ставки в рекламе

Формат ответа (строго JSON):
{
  "by_rule": [
    {
      "case": "описание кейса",
      "rule_type": "тип правила (price_adjust, content_ticket, ads_bid_adjust)",
      "confidence": 0.9
    }
  ],
  "new": [
    {
      "case": "описание нового кейса", 
      "suggested_rule": {
        "condition_type": "ratio",
        "condition_params": {"drop_pct": 0.15, "min_samples": 5},
        "action_type": "new_action",
        "action_params": {"param1": "value1"},
        "severity": "high"
      },
      "confidence": 0.8,
      "rationale": "обоснование нового правила"
    }
  ]
}"""

        user_prompt = f"""
ТРАНСКРИПТ СОЗВОНА:
{transcript}

СУЩЕСТВУЮЩИЕ ПРАВИЛА:
{algorithm_preview or "Правила не предоставлены"}

Проанализируй транскрипт и верни JSON с найденными решениями."""

        return system_prompt, user_prompt
    
    def extract_proposals(self, transcript: str, algorithm_preview: str = None) -> List[Proposal]:
        """Извлекает предложения из транскрипта"""
        if not self.client:
            print("❌ OpenAI клиент не настроен")
            return []
        
        try:
            system_prompt, user_prompt = self._get_prompt(transcript, algorithm_preview)
            
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            proposals = []
            
            # Обрабатываем решения по существующим правилам
            for item in data.get("by_rule", []):
                proposal = Proposal(
                    call_date=self._get_current_date(),
                    extracted_case=item.get("case", ""),
                    existing_rule_matched=True,
                    suggested_rule_diff="",
                    confidence=item.get("confidence", 0.5),
                    notes=f"Соответствует правилу: {item.get('rule_type', '')}"
                )
                proposals.append(proposal)
            
            # Обрабатываем новые решения
            for item in data.get("new", []):
                proposal = Proposal(
                    call_date=self._get_current_date(),
                    extracted_case=item.get("case", ""),
                    existing_rule_matched=False,
                    suggested_rule_diff=json.dumps(item.get("suggested_rule", {}), ensure_ascii=False, indent=2),
                    confidence=item.get("confidence", 0.5),
                    notes=item.get("rationale", "")
                )
                proposals.append(proposal)
            
            print(f"✅ Извлечено {len(proposals)} предложений из транскрипта")
            return proposals
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON ответа: {e}")
            return []
        except Exception as e:
            print(f"❌ Ошибка извлечения предложений: {e}")
            return []
    
    def _get_current_date(self) -> str:
        """Возвращает текущую дату в ISO формате"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def extract_from_multiple_transcripts(self, transcripts: List[Dict[str, str]], 
                                        algorithm_preview: str = None) -> List[Proposal]:
        """Извлекает предложения из нескольких транскриптов"""
        all_proposals = []
        
        for transcript_info in transcripts:
            filename = transcript_info.get("filename", "unknown")
            content = transcript_info.get("content", "")
            
            if not content:
                print(f"⚠️ Пропускаем пустой файл: {filename}")
                continue
            
            print(f"🔍 Обрабатываем транскрипт: {filename}")
            proposals = self.extract_proposals(content, algorithm_preview)
            
            # Добавляем информацию о файле к предложениям
            for proposal in proposals:
                proposal.notes += f" | Источник: {filename}"
            
            all_proposals.extend(proposals)
        
        print(f"✅ Всего извлечено {len(all_proposals)} предложений из {len(transcripts)} транскриптов")
        return all_proposals


# Глобальный экземпляр
llm_extractor = LLMExtractor()
