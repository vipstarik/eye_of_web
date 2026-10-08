# 📊 Аудит данных EyeOfWeb

**Дата:** 2026-10-08 · **Ветка:** `arena/235fafb5-eye-of-web` · **Ревизия до правок:** `943644f`

Проверено соответствие данных во всём проекте: схема PostgreSQL (`sql/schema.sql`,
`sql/users.sql`), схема Milvus (`MILVUS_SCHEMA_GENERATOR.py`), все SQL-запросы в Python-коде,
конфигурация (env / `config.json` / docker-compose / документация) и список зависимостей.

---

## 🔬 Как проверялось (воспроизводимо)

1. **Извлечение SQL из кода.** AST-обходом `src/**/*.py` вытащены все строковые литералы,
   содержащие SQL (включая f-строки): **170 операторов**.
2. **Реальное исполнение.** Схема из `sql/schema.sql` + `sql/users.sql` развёрнута в
   настоящем PostgreSQL (WASM-сборка `@electric-sql/pglite`, 20 таблиц создано), и каждый
   из 170 операторов выполнен против неё.
3. **Статическая сверка** через `sqlglot` (таблицы/колонки против DDL) — как второй,
   независимый проход.
4. **Сверка конфигов**: `os.environ.get(...)` по всему коду ↔ `docker-compose.yml` ↔ README/DOCKER.md.
5. **Сверка зависимостей**: все `import` ↔ `requirements*.txt` + Dockerfile.

Результат исполнения 170 операторов **после** внесённой правки:

| Результат | До правки | После правки |
|---|---|---|
| Успешно | 90 | **92** |
| Ошибка схемы (нет таблицы/колонки) | 29 | **25** |
| Прочие ошибки (артефакт подстановки `NULL` в параметры) | 51 | 53 |

Из 25 «ошибок схемы» 3 — ложные срабатывания: имя таблицы подставляется через f-строку
(`migration_to_milvus.py:283`, `migration_to_milvus.py:382`, `app/routes/web.py:1324`).
**Реальных дефектов — 22 оператора.**

> Ограничение проверки: расширение `pgvector` в pglite недоступно
> (`extension "vector" is not available`), поэтому `CREATE EXTENSION IF NOT EXISTS "vector"`
> исполнить не удалось. На выводы это не влияет — все найденные ошибки относятся к
> отсутствующим таблицам/колонкам, а не к векторным операторам.

---

## ✅ Исправлено сейчас

**`src/lib/database_tools.py`, функция `insertPageBased()` (def на строке 595)** — единственный
путь записи данных о просканированных страницах. Использовались имена колонок, которых нет в схеме:

| Строка | Было | Стало (по `sql/schema.sql`) |
|---|---|---|
| 677 | `"BaseDomainID" WHERE "BaseDomain"` | `"BaseDomainID" WHERE "Domain"` |
| 683 | `INSERT INTO "BaseDomainID" ("BaseDomain")` | `INSERT INTO "BaseDomainID" ("Domain")` |
| 698 | `"WebSiteCategoryID" WHERE "CategoryName"` | `"WebSiteCategoryID" WHERE "Category"` |
| 704 | `INSERT INTO "WebSiteCategoryID" ("CategoryName")` | `INSERT INTO "WebSiteCategoryID" ("Category")` |

Доказательство корректности имён: в том же файле остальные обращения уже используют правильные
имена — строки 361, 375, 497, 932, 938, 950, 956 (`"Domain"`) и 994 (`"Category"`).

**Проверка правки:** повторный прогон того же исполнителя.
До: `column "BaseDomain" does not exist` / `column "CategoryName" does not exist`.
После: оба `SELECT` проходят полностью, оба `INSERT` доходят до стадии выполнения и падают
только на `null value in column "Domain" ... violates not-null constraint` — ровно как их
заведомо корректные аналоги на строках 375, 938, 956, 1000 (этот NOT NULL — артефакт
подстановки `NULL` вместо параметра в проверке). Счётчик ошибок схемы: 29 → 25.

**Влияние:** `insertPageBased` вызывают 4 краулера — `lib/news_crawler.py:155`,
`lib/single_domain_playwright_crawler.py:169`, `lib/single_domain_selenium_thread.py:187`,
`lib/single_domain_thread.py:252`. До правки любой вызов с номером телефона/e-mail падал на
`UndefinedColumn`, и данные страницы не сохранялись.

---

## ⚠️ Требует решения: остатки миграции в Milvus

Первичная схема хранила векторы и атрибуты лица в PostgreSQL. `migration_to_milvus.py` перенёс
их в Milvus и удалил колонки (`"drop_sql_columns"`), но часть кода всё ещё обращается к старым
колонкам в PostgreSQL. Ниже — фактические ошибки PostgreSQL при исполнении кода из репозитория.

### A. Загрузчики пишут в несуществующие колонки (9 операторов)

`column "FaceEmbeddingData" of relation "..." does not exist`

| Файл:строка | Таблица |
|---|---|
| `db_gui_qt.py:477, 500, 520, 542` | EgmArananlar, WhiteListFaces, CustomFaceStorage, ExternalFaceStorage |
| `db_gui_uploader.py:470, 493, 513, 535` | те же четыре |
| `general_whitelist_loader.py:79` | WhiteListFaces |

Все три инструмента вставляют `FaceEmbeddingData, Landmarks2d, FaceBox, DetectionScore,
FaceGender, FaceAge` — этих колонок в схеме больше нет, и в Milvus эти скрипты не пишут вовсе
(`milvus` в них не упоминается). Итог: загрузка лиц через GUI/лоадер невозможна.
Варианты: (1) писать векторы в соответствующие Milvus-коллекции и `MilvusID` в SQL,
(2) добавить недостающие колонки обратно в схему.

### B. Веб-роуты читают атрибуты лица из PostgreSQL (7 операторов)

| Файл:строка | Роут | Отсутствующие колонки `EyeOfWebFaceID` |
|---|---|---|
| `app/routes/web.py:2345` | `/fetch_domain_faces` | `FaceBox` |
| `app/routes/web.py:2524` | `/deep_insight/<face_id>` | `FaceGender`, `FaceAge`, `DetectionScore`, `FaceBox` |
| `app/routes/web.py:2702` | `/face_similarity_analysis/<face_id>` | `FaceEmbeddingData`, `FaceGender`, `FaceAge` |
| `app/routes/web.py:2796` | `/face_similarity_analysis/<face_id>` | `FaceBox` |
| `app/routes/web.py:4771, 4788` | `/download/relationship_details_report/...` | `FaceEmbeddingData` |
| `app/routes/web.py:4961` | `/download/relationship_details_report/...` | `FaceBox` |

В схеме `EyeOfWebFaceID` содержит только `ID`, `MilvusRefID`, `DetectionDate`. Все эти данные
лежат в Milvus-коллекции `EyeOfWebFaceDataMilvus`. В `lib/database_tools.py` уже есть готовые
хелперы для чтения по `pg_face_id` — `get_milvus_face_attributes` (def 3475),
`get_batch_milvus_face_attributes` (def 3809) и `find_similar_face_ids_in_milvus` (def 3602);
роуты стоит перевести на них.

### C. Функции поиска «похожих лиц» (2 оператора)

- `lib/database_tools.py:2121`, функция `searchEgmArananlar` (def 2096), вызывается из
  `app/controllers/search_controller.py:588`:
  `column "DetectionScore" does not exist` (также `FaceGender`, `FaceAge`).
- `lib/database_tools.py:2891`, функция `findSimilarWhiteListFaces` (def 2864), вызывается из
  `app/controllers/search_controller.py:161`:
  `column "DetectionScore" does not exist`; кроме того запрос использует pgvector-оператор `<=>`
  по колонке `FaceEmbeddingData`, которой в схеме нет.

Для сравнения: соседние `searchWhiteListFaces` (def 1790) и `searchExternalFaces` уже корректно
переведены на «только SQL» и проверку проходят.

### D. Мёртвый код и dev-скрипты (4 оператора)

| Файл:строка | Ошибка | Комментарий |
|---|---|---|
| `lib/database_tools.py:2232` (`getFaceDetailsWithLandmarks`) | `relation "faces" does not exist` | вызовов нет |
| `lib/database_tools.py:2280` (`getWhitelistFaceDetailsWithLandmarks`) | `relation "whitelistfaces" does not exist` | snake_case-колонки, вызовов нет |
| `lib/database_tools.py:2327` (`getEgmFaceDetailsWithLandmarks`) | `relation "egmwantedfaces" does not exist` | вызовов нет |
| `verify_facebox_scale.py:21` | `column "ImageID" does not exist` | отладочный скрипт |

---

## 🚨 Отдельно: несуществующий метод `findSimilarEgmFaces`

Метод вызывается в двух живых местах, но **не определён нигде в репозитории**
(`grep -rn "def findSimilarEgmFaces"` → пусто):

- `app/controllers/search_controller.py:183`
- `app/routes/web.py:1692` (роут `/egm_search_by_face/<face_id>`)

Оба вызова обёрнуты в `try/except`, поэтому вместо ошибки пользователь получает пустой результат
поиска по базе EGM. Единственное упоминание имени — строка лога
`lib/database_tools.py:2216` (`print(f"findSimilarEgmFaces hata: ...")`) внутри
`searchEgmArananlar`, то есть метод, судя по всему, был переименован без правки вызовов.

---

## ⚙️ Конфигурационные данные

| Что | Значения в разных местах | Комментарий |
|---|---|---|
| Версия приложения | `lib/env.py:19` → `2.3.1`; `generate_config.py:17` → `2.1.0`; `doc/CHANGELOG.md` → `[2.3.1]` | `config.json`, генерируемый в контейнере, получает устаревшую версию |
| Пароль админа по умолчанию | `docker-compose.yml:23` → `admin123_changeme`; `generate_config.py:52` и `run.py:332` → `admin123`; `app/config/config.py:12` → `golfalfa`; README/CHANGELOG → `admin123_changeme` / `admin123` | три разных значения по умолчанию; фактически используется `config.json` → `initial_admin_user` |
| Учётные данные Milvus | `lib/database_tools.py:38-41` читает `MILVUS_USER` / `MILVUS_PASSWORD`; `MILVUS_SCHEMA_GENERATOR.py:31` подключается **без** `user`/`password` | при включённой авторизации (`src/user.yaml`, `milvus_password_set.py`) генератор схемы на старте контейнера не сможет подключиться |
| `ALLOWED_HOSTS` | `lib/env.py:37` = `["localhost", "127.0.0.1"]`, файл помечен «DONT CHANGE IT»; `run.py:454-465` отвечает `403` на любой другой Host | недоступно извне по домену/LAN-адресу; список не настраивается через env |

Отдельно: `CREATE EXTENSION IF NOT EXISTS "vector"` в `sql/schema.sql` теперь нужен только
одному сломанному запросу (пункт C). После его перевода на Milvus зависимость от `pgvector`
(и образ `pgvector/pgvector:pg16` в docker-compose) становится необязательной.

---

## 📦 Зависимости

Импорты, для которых нет записи ни в одном `requirements*.txt` и ни в одном Dockerfile:

| Модуль | Где используется | Статус |
|---|---|---|
| `googlesearch` | `google_rss_dumper.py:1` (без try/except) | **ImportError**; в `twitter_crawler_google_based.py:30` обёрнут в try/except |
| `colorlog` | `pyrogram_telegram_crawler_main.py:14`, `telethon_telegram_crawler_main.py` (без try/except) | **ImportError** |
| `scipy` | `app/routes/web.py:39` (импорт верхнего уровня) | работает только транзитивно через `scikit-learn`; не объявлен |
| `wtforms` | `app/forms.py`, `app/routes/admin.py` | транзитивно через `Flask-WTF`; не объявлен |
| `jwt` (PyJWT) | `app/controllers/user_controller.py` | транзитивно через `Flask-JWT-Extended`; не объявлен |
| `urllib3` | `lib/url_image_download.py`, `lib/css_image_extractor/css.py` | транзитивно через `requests`; не объявлен |
| `torch` | `run.py`, `lib/similarity_utils.py` | корректно: обёрнут в try/except, ставится отдельно в Dockerfile |
| `PyQt5`, `tkinter` | `db_gui_qt.py`, `realtime_search_camera.py`, `db_gui_uploader.py` | GUI-утилиты, в серверные требования не входят |
| `stdlib_list` | только `scan_imports.py` | сам `scan_imports.py` нерабочий: путь `/home/charlie/opt/eye_of_web/src` захардкожен |

---

## ✅ Что проверку прошло

- **Таблица `users`** — все 11 SQL-операций над ней (`app/controllers/user_controller.py:32,
  86, 130, 151, 169, 227, 285, 323, 357` и `run.py:237, 248`) соответствуют `sql/users.sql`:
  колонок-фантомов нет. Динамический `UPDATE` на строке 285 собирает только захардкоженные
  фрагменты вида `"username = %s"`, значения передаются параметрами.
  `app/routes/admin.py` собственного SQL не содержит — работает через `UserController`.
- **92 SQL-оператора** выполняются против схемы без ошибок — в том числе весь путь
  `insertImageBased`, `CrawledAddress`, `ImageHashID`, `ImageID`, `UrlPathID`, `UrlEtcID`,
  `ImageUrlPathID`, `ImageUrlEtcID`, `ImageTitleID`, `PhoneNumberID`, `EmailAddressID`,
  `PageBasedMain`, `ImageBasedMain`, `BaseDomainID`, `WebSiteCategoryID`.
- **Milvus**: имена полей во всех `output_fields` / `insert` основного приложения
  (`face_embedding_data`, `landmarks_2d`, `face_box`, `detection_score`, `face_gender`,
  `face_age`, `detection_date_ts`, `id`) совпадают со схемой `EyeOfWebFaceDataMilvus`.
- **SQL-инъекций не найдено**: все запросы с пользовательскими данными параметризованы (`%s`).
  f-строки в SQL подставляют только внутренние значения (списки плейсхолдеров, имена таблиц
  из конфигурации миграции) — не пользовательский ввод.
- **Инъекции в env**: все переменные из `docker-compose.yml` либо читаются кодом, либо
  предназначены для самих сервисов (Postgres/etcd/MinIO) и для shell-entrypoint (`INIT_SCHEMA`).

---

## 🔁 Как повторить проверку

Инструменты аудита лежат вне git (в рабочей области, каталог `audit/`):

```bash
# 1. статическая сверка схемы и SQL
python3 audit/sql_schema_audit.py

# 2. извлечение SQL из кода + исполнение против реальной схемы PostgreSQL
python3 audit/extract_queries.py
cd audit/pg && node run.mjs

# 3. сверка зависимостей и env-переменных
python3 audit/deps_check.py
python3 audit/env_check.py
```

---

## ➕ Дополнение (второй ход): миграция роутов и поиска на Milvus

Выполнены пункты **B** и **C** из основного аудита. Код переведён с несуществующих
PostgreSQL-колонок на Milvus через существующие/новые хелперы.

**Изменения в `lib/database_tools.py`:**
- Добавлен общий хелпер `_query_milvus_entities_by_ids()` (чтение из Milvus по списку Milvus ID).
- `searchEgmArananlar()` больше не читает `DetectionScore/FaceGender/FaceAge` из SQL — они
  берутся из `EgmArananlarMilvus` по `MilvusID` (SELECT теперь только существующие колонки).
- `findSimilarWhiteListFaces()` переписан: векторный поиск в `WhiteListFacesMilvus`, мета-данные
  и картинка — из SQL по `MilvusID` (pgvector больше не используется).
- Добавлен отсутствовавший метод `findSimilarEgmFaces()` (поиск в `EgmArananlarMilvus`) —
  вызовы в `search_controller.py:183` и `web.py` теперь попадают в существующий метод.
- Общий рабочий метод `_find_similar_in_collection()`.

**Изменения в `app/routes/web.py`** (чтение атрибутов лица переведено на Milvus-хелперы):
- `/fetch_domain_faces`, `/deep_insight/<id>`, `/face_similarity_analysis/<id>`,
  `/download/relationship_details_report/...` — `FaceBox/FaceEmbeddingData/FaceGender/FaceAge/
  DetectionScore` теперь читаются из `EyeOfWebFaceDataMilvus`
  (`get_milvus_face_attributes` / `get_batch_milvus_face_attributes`), SQL отдаёт только
  URL-компоненты и risk. Добавлена обработка facebox и как списка (Milvus), и как строки (legacy).

**Проверка:** тот же исполнитель (166 операторов после правок): успешно **96**, ошибок схемы **17**.
Из 17: 9 — loaders (группа A, оставлена осознанно), 3 — мёртвый код `get*DetailsWithLandmarks`,
1 — dev-скрипт `verify_facebox_scale.py`, 4 — артефакты f-строк с динамическими именами таблиц
(`migration_to_milvus.py`, `web.py:1324`, `_find_similar_in_collection`). **Ни одной точки B/C не осталось.**

**Пункт 1 (прогон фото):** в песочнице невозможен — байты вложения не материализованы
(`uploads/` отсутствует), а веса InsightFace лежат на `*.githubusercontent.com` (вне разрешённых
хостов). Подготовлен `audit/face_pipeline_test.py` (детекция + сверка размерностей 512/212/4
со схемой Milvus) для запуска в окружении с доступом к весам; локально выполнена только лёгкая
Haar-детекция как sanity-check инструмента.

**Пункт 3 (почему код не «найдёт соцсети человека»)** — см. раздел ниже.

### Архитектура: почему платформа не ищет человека в интернете

1. **Поиск = сопоставление с внутренними базами.** `find_similar_face_ids_in_milvus()`,
   `findSimilarWhiteListFaces()`, `findSimilarEgmFaces()` ищут вектор только в локальных
   коллекциях Milvus (сканированные сайты, whitelist, EGM). Никакого внешнего «кто это» нет:
   если лица нет в ваших базах, совпадений не будет.
2. **Краулеры — сбор по заданным URL, а не идентификация.** `facebook_*`, `twitter_*`,
   `linkedin_*`, `google_*` собирают данные/изображения с указанных доменов и кладут их в
   PostgreSQL+Milvus. Они не принимают «фото → найти профиль»; входа «лицо» у них нет.
3. **Нет модуля face→profile.** Нет ни таблицы/коллекции, сопоставляющей лицо аккаунтам
   соцсетей, ни внешнего reverse-image-API. Связка «эмбеддинг ↔ соцсеть» в модели данных
   отсутствует (см. `sql/schema.sql` и `MILVUS_SCHEMA_GENERATOR.py`).
4. **Юридический контур.** README/дисклеймер ограничивают применение академическими целями;
   поиск реального человека по соцсетям вышел бы за рамки и KVKK/GDPR.

Итог: «найти соцсети человека по фото» требует внешнего сервиса идентификации, которого в
архитектуре нет и который не следует добавлять для частных лиц.
