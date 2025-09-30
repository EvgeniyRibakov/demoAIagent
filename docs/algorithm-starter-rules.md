# Стартовые правила для листа Algorithm

## На основе метрик из шаблона таблицы

### R001 - Конверсия в корзину
- **RuleId**: R001
- **Block**: funnel
- **Metric**: Конверсия в корзину, %
- **ConditionType**: ratio
- **ConditionParams**: {"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}
- **ActionType**: price_adjust
- **ActionParams**: {"competitor_scan":"on","target_delta_pct":"match_top3-1%","floor_margin_pct":12}
- **Severity**: high
- **AutoApply**: N
- **Active**: Y

### R002 - CTR (Click-Through Rate)
- **RuleId**: R002
- **Block**: ads
- **Metric**: CTR
- **ConditionType**: ratio
- **ConditionParams**: {"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}
- **ActionType**: content_ticket
- **ActionParams**: {"task":"replace_main_image","priority":"high","assignee":"content_manager"}
- **Severity**: medium
- **AutoApply**: N
- **Active**: Y

### R003 - Переходы в карточку
- **RuleId**: R003
- **Block**: funnel
- **Metric**: Переходы в карточку
- **ConditionType**: ratio
- **ConditionParams**: {"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}
- **ActionType**: ads_bid_adjust
- **ActionParams**: {"target":"clicks","delta":"-10% to +10%","guard":"acos<=0.3"}
- **Severity**: medium
- **AutoApply**: N
- **Active**: Y

### R004 - Положили в корзину
- **RuleId**: R004
- **Block**: funnel
- **Metric**: Положили в корзину
- **ConditionType**: ratio
- **ConditionParams**: {"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}
- **ActionType**: price_adjust
- **ActionParams**: {"competitor_scan":"on","target_delta_pct":"match_top3-2%","floor_margin_pct":10}
- **Severity**: high
- **AutoApply**: N
- **Active**: Y

### R005 - CR (Conversion Rate)
- **RuleId**: R005
- **Block**: funnel
- **Metric**: CR
- **ConditionType**: ratio
- **ConditionParams**: {"baseline":"rolling_7d","drop_pct":0.1,"min_samples":5}
- **ActionType**: content_ticket
- **ActionParams**: {"task":"review_product_description","priority":"high","assignee":"content_manager"}
- **Severity**: high
- **AutoApply**: N
- **Active**: Y

### R006 - Показы
- **RuleId**: R006
- **Block**: ads
- **Metric**: Показы
- **ConditionType**: ratio
- **ConditionParams**: {"baseline":"rolling_7d","drop_pct":0.3,"min_samples":5}
- **ActionType**: ads_budget_adjust
- **ActionParams**: {"target":"impressions","delta":"+20%","max_budget_increase":5000}
- **Severity**: low
- **AutoApply**: N
- **Active**: Y

## Как добавить в таблицу

1. Откройте лист `Algorithm` в Google Таблице
2. Скопируйте значения из таблицы выше (начиная с R001)
3. Вставьте в соответствующие колонки:
   - A: RuleId
   - B: Block  
   - C: Metric
   - D: ConditionType
   - E: ConditionParams
   - F: ActionType
   - G: ActionParams
   - H: Severity
   - I: AutoApply
   - J: Active

## Примечания

- **baseline**: "rolling_7d" означает среднее за последние 7 дней
- **drop_pct**: порог падения в долях (0.15 = 15%)
- **min_samples**: минимальное количество точек для анализа
- **AutoApply**: "N" означает, что требуется ручное подтверждение
- **Active**: "Y" означает, что правило активно

Метрики должны точно совпадать с названиями в колонке B вашего шаблона таблицы.
