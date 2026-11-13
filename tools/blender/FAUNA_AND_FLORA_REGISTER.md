# Реестр фауны и флоры — поштучные ассеты

Источник перечня: Official Satisfactory Wiki, страницы Creatures/Fauna и Category:Flora. Варианты и исторически удалённые формы отделены от актуальных игровых существ.

## Фауна

| Asset ID | Игровое название | Вариант / состояние | Отдельный меш | Статус |
|---|---|---|---|---|
| fauna-lizard-doggo | Lizard Doggo | основной | да | planned |
| fauna-non-flying-bird | Non Flying Bird | наземная птица | да | planned |
| fauna-power-slug-blue | Power Slug | Blue | да | planned |
| fauna-power-slug-yellow | Power Slug | Yellow | да | planned |
| fauna-power-slug-purple | Power Slug | Purple | да | planned |
| fauna-space-giraffe-tick-penguin-whale | Space Giraffe-Tick-Penguin-Whale Thing | основной | да | planned |
| fauna-giant-flying-manta | Giant Flying Manta | основной | да | planned |
| fauna-beetle | Beetle | основной | да | planned |
| fauna-flying-crab-hatcher | Flying Crab Hatcher | обычный | да | planned |
| fauna-elite-flying-crab-hatcher | Elite Flying Crab Hatcher | элитный | да | planned |
| fauna-flying-crab | Flying Crab | летающий | да | planned |
| fauna-spore-flower-creature | Spore Flower | стационарное существо | да | planned |
| fauna-fluffy-tailed-hog | Fluffy-tailed Hog | обычный | да | planned |
| fauna-alpha-hog | Alpha Hog | крупный вариант | да | planned |
| fauna-cliff-hog | Cliff Hog | вариант скалистой местности | да | planned |
| fauna-nuclear-hog | Nuclear Hog | радиоактивный игровой вариант | да | planned |
| fauna-spitter-desert | Spitter | Desert | да | planned |
| fauna-spitter-aquatic | Spitter | Aquatic | да | planned |
| fauna-spitter-forest | Spitter | Forest | да | planned |
| fauna-spitter-red-forest | Spitter | Red Forest | да | planned |
| fauna-alpha-spitter-forest | Alpha Spitter | Forest | да | planned |
| fauna-alpha-spitter-aquatic | Alpha Spitter | Aquatic | да | planned |
| fauna-alpha-spitter-desert | Alpha Spitter | Desert | да | planned |
| fauna-alpha-spitter-red-forest | Alpha Spitter | Red Forest | да | planned |
| fauna-baby-stinger-normal | Baby Stinger | обычный | да | planned |
| fauna-baby-stinger-cave | Baby Stinger | пещерный подтип | отдельный вариант проверить | planned |
| fauna-alpha-stinger | Alpha Stinger | основной | да | planned |
| fauna-elite-gas-stinger | Elite Gas Stinger | основной | да | planned |
| fauna-flying-bird | Flying Bird | сопровождает Manta | да | planned |
| fauna-leaf-bug | Leaf Bug | основной | да | planned |
| fauna-grass-sprite | Grass Sprite | основной | да | planned |
| fauna-cave-bat | Cave Bat | основной | да | planned |

### Исторические / удалённые / неигровые записи

Не смешивать с активным набором игры. Хранить только в справочном реестре, не экспортировать в текущую игровую сборку без отдельного решения:

| Asset ID | Название | Статус |
|---|---|---|
| fauna-walker-legacy | Walker | removed since Update 3 |
| fauna-huge-pink-jellyfish-legacy | Huge Pink Jellyfish | removed in Version 1.0 |
| fauna-lake-shark-legacy | Lake Shark | removed since Update 3 |
| fauna-crab-boss-concept | Crab Boss | never appeared in game |
| fauna-pioneer-reference | Pioneer | персонаж-эталон, не фауна |

## Флора и растительные объекты

| Asset ID | Название в игре / Wiki | Роль | Отдельный меш | Статус |
|---|---|---|---|---|
| flora-bacon-agaric | Bacon Agaric | собираемый пищевой гриб | да | planned |
| flora-beryl-nut | Beryl Nut | собираемый плод | да | planned |
| flora-flower-petals | Flower Petals | собираемый ресурс | да, набор лепестков | planned |
| flora-leaves | Leaves | собираемый ресурс | да, вариации листьев | planned |
| flora-mycelia | Mycelia | грибной/органический ресурс | отдельная ресурсная форма | planned |
| flora-paleberry | Paleberry | собираемый плод | да | planned |
| flora-round-blue-cap-mushroom | Round Blue Cap Mushroom | гриб | да | planned |
| flora-spore-flower | Spore Flower | опасное растение/объект мира | да | planned |
| flora-vine-ladder | Vine ladder | вертикальная растительная структура | да | planned |
| flora-vines | Vines | лианы | набор мешей/вариаций | planned |
| flora-wood | Wood | собираемый древесный ресурс | да | planned |
| flora-general-plant-clusters | Flora | общий класс декора | набор отдельных видов после визуальной инвентаризации | planned |

## Правила моделирования фауны

- Для каждого вида сделать самостоятельную анатомическую базовую сетку и риг.
- Разные игровые варианты должны быть отдельными ассетами или подтверждёнными variant collections; не создавать разные виды только сменой цвета, если силуэт/анатомия отличаются.
- Для каждого существа подготовить idle, locomotion, turn, alert, interaction и death/disabled states только в объёме, соответствующем оригинальному поведению и возрастной безопасности проекта.
- LOD и коллизии делать отдельно от визуальной сетки.
- Не использовать извлечённые игровые модели, текстуры, риги или анимации.

## Правила моделирования флоры

- Собирать отдельные меши для собираемого объекта и крупного растения, если это разные визуальные формы.
- Листва должна иметь дешёвые мобильные LOD и корректный alpha clipping.
- Растения, которые взаимодействуют с окружением, получают collision proxy и точки сбора.
- Ресурсный предмет в инвентаре/на конвейере может быть отдельным мешем от большого растения в мире.

## Источники

- https://satisfactory.wiki.gg/wiki/Creatures
- https://satisfactory.wiki.gg/wiki/Category:Fauna
- https://satisfactory.wiki.gg/wiki/Category:Flora
- https://satisfactory.wiki.gg/wiki/Lizard_Doggo

## Ограничение проверки

Категория Flora включает 14 страниц, но среди них есть обзорная страница, исторические записи и записи ресурсов. Категория Fauna содержит 22 страницы, включая исторические/концептуальные записи. Реестр отделяет актуальные игровые меши от удалённых и справочных объектов. Варианты, для которых Wiki не подтверждает самостоятельную геометрию, помечены как требующие проверки по игровым референсам.
