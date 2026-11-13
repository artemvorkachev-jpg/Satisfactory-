# Дополнение к реестру Items — пропущенные небоевые позиции

Основано на индексируемом перечне Official Satisfactory Wiki Category:Items. Это дополнение нужно объединить с ITEMS_AND_NONCOMBAT_EQUIPMENT_REGISTER.md при следующей редакции. Список не включает ограниченные категории предметов.

| Asset ID | Название | Семейство | Статус |
|---|---|---|---|
| item-biomass | Biomass | биотопливо | planned |
| item-bauxite | Bauxite | руда | planned |
| item-caterium-ore | Caterium Ore | руда | planned |
| item-coal | Coal | руда/топливо | planned |
| item-compacted-coal | Compacted Coal | топливо | planned |
| item-copper-ore | Copper Ore | руда | planned |
| item-hard-drive | Hard Drive | исследовательский предмет | planned |
| item-iron-ore | Iron Ore | руда | planned |
| item-limestone | Limestone | руда | planned |
| item-miner | Miner | строительный объект/инвентарная запись | отдельный ID модели для Mk.1/Mk.2/Mk.3 | planned |
| item-power-slug | Power Slug | исследовательский ресурс | три визуальных варианта | planned |
| item-quickwire | Quickwire | проводник | planned |
| item-raw-quartz | Raw Quartz | руда | planned |
| item-sam | SAM | руда | planned |
| item-uranium | Uranium | руда | planned |
| item-uranium-fuel-rod | Uranium Fuel Rod | энергетический компонент | planned |
| item-uranium-waste | Uranium Waste | отход | planned |
| item-wire | Wire | проводник | planned |
| item-biomass-organic-variants | Biomass | визуальные источники биомассы | варианты по подтверждённым видам | planned |

## Исправления к предыдущему списку

- Руды и сырьё не следует дублировать между Items и Resources как две независимые модели, если у них один и тот же визуальный меш. Вместо этого один asset_id может иметь несколько игровых категорий и мест использования.
- Miner — это прежде всего здание с Mk.1/Mk.2/Mk.3, а не обычный предметный меш инвентаря. Запись нужно связать с реестром зданий.
- Power Slug требует трёх вариантов внешнего вида (Blue, Yellow, Purple), а не одной универсальной модели.
- Hard Drive должен иметь отдельную модель исследовательского предмета.
- Quickwire и Wire должны быть отдельными моделями, не объединять их с Cable.
- Для Biomass отдельно определить игровой вид предмета и исходные органические формы, из которых он получен.
