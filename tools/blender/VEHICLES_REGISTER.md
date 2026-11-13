# Реестр транспорта и транспортных ассетов

Источник: Official Satisfactory Wiki — Vehicles, Transportation и связанные страницы зданий. В игре есть семь основных транспортных типов/классов: Tractor, Truck, Explorer, Cyber Wagon, Factory Cart, Trains и Drones. Поезд разбивается на локомотив и вагоны; транспортная инфраструктура получает отдельные ассеты.

## A. Колёсный транспорт

| Asset ID | Название | Самостоятельные варианты/части | Статус |
|---|---|---|---|
| vehicle-tractor | Tractor | кузов, кабина, рама, колёса, подвеска | planned |
| vehicle-truck | Truck | кабина, грузовая платформа, колёса, подвеска | planned |
| vehicle-explorer | Explorer | кузов, кабина, колёса, подвеска, свет | planned |
| vehicle-cyber-wagon | Cyber Wagon | кузов, колёса, световые элементы | planned |
| vehicle-factory-cart | Factory Cart | корпус, колёса, сиденье/управление | planned |
| vehicle-golden-factory-cart | Golden Factory Cart | отдельный косметический вариант, если подтверждён в выбранной версии | planned |

## B. Железнодорожный транспорт

| Asset ID | Название | Самостоятельные варианты/части | Статус |
|---|---|---|---|
| vehicle-electric-locomotive | Electric Locomotive | корпус, кабина, тележки, колёса, сцепки | planned |
| vehicle-freight-car | Freight Car | грузовой вагон, тележки, сцепки | planned |
| vehicle-fluid-freight-car | Fluid Freight Car | жидкостный вагон/резервуар, тележки, соединения | verify version-specific name |
| vehicle-train-wheelset | Train Wheelset | отдельная общая деталь | planned |
| vehicle-train-coupler | Train Coupler | сцепка | planned |

## C. Воздушный транспорт

| Asset ID | Название | Самостоятельные варианты/части | Статус |
|---|---|---|---|
| vehicle-drone | Drone | центральный корпус, роторы, посадочные опоры, грузовой отсек | planned |
| vehicle-drone-rotor | Drone Rotor Assembly | отдельный вращающийся узел | planned |
| vehicle-drone-cargo-container | Drone Cargo Container | грузовой контейнер/крепление | planned |

## D. Станции и инфраструктура

| Asset ID | Название | Самостоятельные варианты/части | Статус |
|---|---|---|---|
| station-truck | Truck Station | корпус, док, погрузочная зона | planned |
| station-fluid-truck | Fluid Truck Station | жидкостные патрубки, док и резервуарная часть | planned |
| station-drone-port | Drone Port | площадка, корпус, топливный/грузовой интерфейс | planned |
| station-train | Train Station | платформа, здание, интерфейсы | planned |
| station-freight-platform | Freight Platform | погрузочная рама и механизмы | planned |
| station-fluid-freight-platform | Fluid Freight Platform | жидкостные соединения и платформа | planned |
| station-empty-platform | Empty Platform | базовая платформа | planned |
| railway-track | Railway | прямые, кривые, уклоны и переходы | planned |
| railway-support | Railway Supports | опоры и эстакады | planned |
| railway-block-signal | Block Signal | сигнальный объект | planned |
| railway-path-signal | Path Signal | сигнальный объект | planned |
| railway-switch-control | Railroad Switch Control | управление стрелкой | planned |
| vehicle-path-node | Vehicle Path Node | маркер/узел маршрута | planned |
| vehicle-fuel-port | Vehicle Fuel Port | станционный топливный интерфейс, если он визуально отдельный | planned |

## E. Общие требования

- Все колёса, оси, подвески и тележки должны быть совместимы с размерами конкретного транспорта.
- Транспорт должен иметь pivot по центру физической массы и отдельные точки контакта колёс.
- Для поезда проверить ширину колеи, высоту платформы и сцепки на общем эталоне.
- Для дрона проверить габарит посадочной площадки, высоту шасси и безопасный клиренс роторов.
- Топливные интерфейсы и грузовые порты моделировать как самостоятельные соединительные элементы, если это отдельная геометрия.
- Движение и логистика транспорта должны работать независимо от того, виден ли транспорт в кадре.
- Для мобильной версии сделать LOD и упрощённые коллизии; не отключать расписания, маршруты и перемещение груза за кадром.

## Источники

- https://satisfactory.wiki.gg/wiki/Vehicles
- https://satisfactory.wiki.gg/wiki/Train
- https://satisfactory.wiki.gg/wiki/Drone
- https://satisfactory.wiki.gg/wiki/Truck_Station
- https://satisfactory.wiki.gg/wiki/Train_Station
- https://satisfactory.wiki.gg/wiki/Transportation
