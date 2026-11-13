# Реестр ресурсных узлов и собираемых природных объектов

Источник: Official Satisfactory Wiki — Resource Node / Nodes. Сверка охватывает визуальные ресурсные семейства, их узлы и ручные залежи. Все размеры и местоположения конкретных узлов должны быть измерены по внутриигровой карте/референсам; здесь фиксируются только типы ассетов.

| Asset ID | Название | Геометрия/вариант | Статус |
|---|---|---|---|
| node-iron-ore | Iron Ore Resource Node | Impure / Normal / Pure | planned |
| deposit-iron-ore | Iron Ore Resource Deposit | отдельная ручная залежь | planned |
| node-copper-ore | Copper Ore Resource Node | Impure / Normal / Pure | planned |
| deposit-copper-ore | Copper Ore Resource Deposit | отдельная ручная залежь | planned |
| node-limestone | Limestone Resource Node | Impure / Normal / Pure | planned |
| deposit-limestone | Limestone Resource Deposit | отдельная ручная залежь | planned |
| node-coal | Coal Resource Node | Impure / Normal / Pure | planned |
| node-caterium-ore | Caterium Ore Resource Node | подтверждённые уровни чистоты | planned |
| deposit-caterium-ore | Caterium Ore Resource Deposit | если присутствует в конкретном варианте узла | planned |
| node-raw-quartz | Raw Quartz Resource Node | Impure / Normal / Pure | planned |
| deposit-raw-quartz | Raw Quartz Resource Deposit | отдельная ручная залежь | planned |
| node-sulfur | Sulfur Resource Node | Impure / Normal / Pure | planned |
| deposit-sulfur | Sulfur Resource Deposit | отдельная ручная залежь | planned |
| node-bauxite | Bauxite Resource Node | Impure / Normal / Pure | planned |
| node-sam | SAM Resource Node | Impure / Normal / Pure | planned |
| node-crude-oil | Crude Oil Resource Node | Impure / Normal / Pure | planned |
| node-resource-well-main | Resource Well Main Node | центральная точка скважины | planned |
| node-resource-well-satellite | Resource Well Satellite Node | отдельный спутниковый узел | planned |
| node-geyser | Geyser | геотермальная точка | planned |
| deposit-boulder-cracked | Cracked Resource Boulder | блокирующий валун, отдельный природный меш | planned |
| deposit-gas-pillar | Gas Pillar | природный газовый столб/объект среды | planned |

## Варианты и геометрия

- Чистота узла (Impure / Normal / Pure) влияет на производительность, но не должна автоматически означать три разных меша, если геометрия одинакова. Хранить как визуальный/material variant только если референс подтверждает визуальное отличие.
- Resource Node и Resource Deposit — разные объекты: узел остаётся после удаления поверхностной залежи.
- Resource Well состоит из центрального узла и окружающих спутниковых точек.
- Geyser — отдельный тип природной точки, не смешивать с рудным узлом.
- Для крупных треснувших валунов и блокирующих природных объектов нужны самостоятельные меши, независимо от ресурса под ними.
- Не делать точные координаты или габариты узлов по приблизительным изображениям. Для конкретной карты требуется отдельная проверка world map и внутриигровых референсов.

## Общие ресурсные меши

Отдельные меши предметов на конвейере и в инвентаре связать с соответствующим сырьём, не создавать дубликат без причины:
- Iron Ore, Copper Ore, Limestone, Coal, Caterium Ore, Raw Quartz, Sulfur, Bauxite, SAM.
- Для слитков и переработанных компонентов использовать записи из ITEMS_AND_NONCOMBAT_EQUIPMENT_REGISTER.md и ITEMS_REGISTER_ADDENDUM.md.

## Источник

https://satisfactory.wiki.gg/wiki/Resource_Node

На странице Resource Node подтверждаются три уровня чистоты для узлов и отдельная сущность Resource Deposit; таблица перечисляет типы рудных ресурсов, Crude Oil, Resource Wells и Geysers. Доступная категория также отмечает, что Resource Deposits — отдельные ручные залежи, а не постоянные автоматические узлы.
