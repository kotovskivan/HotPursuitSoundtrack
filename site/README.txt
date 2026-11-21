САЙТ HOT PURSUIT SOUNDTRACK — https://kotovskivan.github.io/HotPursuitSoundtrack/  (адрес будущий: репо еще НЕ создано)
Одна программа и одна страница на NFS Hot Pursuit 2010 и Hot Pursuit Remastered (Ваня 21.11: «для RE и 2010 будет одна страница»).
Собран 21.11.2026 по образцу сайта Heat. Сейчас — «Скоро» (released = no): первый экран, блок NFS Own Music, «Что будет уметь»,
«Что нужно», «Как дела». 14 языков, uk — главный. Переводы — ИИ (Claude).

ПУБЛИКАЦИЯ (первый раз, после «да» Вани) — как у Heat:
  1. gh repo create kotovskivan/HotPursuitSoundtrack --public; папка HotPursuitSoundtrack = main (пока только site\)
  2. ветка gh-pages = site\gotovo (git worktree), GitHub Pages -> gh-pages / root
  3. дальше — opublikovat.cmd (исходник site -> main, gotovo -> gh-pages)
  4. Search Console: файл googleeef38fee5f2ab13e.html уже в static (один на аккаунт); sitemap — tools\google\gapi.py

ВЫПУСК ПРОГРАММЫ
  sajt.txt: released = yes, version / size / versions; teksty: строка «log <версия>»;
  shablon.html: добавить разделы как у Heat — скрины, «Как пользоваться», помощь, «Что нового», окно «Скачать».
  Своя карточка в блоке NFS Own Music станет «Готово» сама. Хаб: igry.txt обе строки hp soon -> ready + hp_version / hp_download / hp_code.

ЧТО ГДЕ
  shablon.html  разметка и стиль (менять — Claude). Стиль — из файлов игры: черный фон, косые плашки и тонкие косые линии
                (экраны загрузки 2010), красный — гонщики, синий — полиция («мигалка» = подпись Soundtrack), жирный курсив капсом.
                Шрифт игры (UI\FONTS Remastered) — DIN-подобный; на сайте Bahnschrift (это DIN 1451, есть в Windows) — файлов шрифта нет.
  sobrat.py     сборщик -> gotovo\  (prosmotr.cmd — http://localhost:8768/)
  teksty\       14 языков. Общие строки (хаб, подвал, кнопки) взяты с сайта Heat, про HP — свои.
  static\video\hero.mp4  фон первого экрана: 26 с, 1280x544, 3,2 МБ, без звука — 7 кусков заставки 2010 (UI\MOVIES\735005.VP6:
                3.75-6.6, 10.25-14.85, 25.02-26.2, 28.65-31.1, 43.1-48.3, 48.5-53.8, 53.95-58.5 с) — без логотипов EA / Criterion,
                надписи PROTECT & SERVE и кадров-вспышек (черные / белые кадры-склейки искал по яркости, YAVG < 20 / > 200).
                VP6 ffmpeg читает только с начала (перемотка -ss ломает декодер) — сначала весь ролик в mp4, потом резать.
                Ролики Remastered — Bink 2 (KB2j), ffmpeg их не читает.
  static\img\bg.jpg      постер до видео (первый кадр hero.mp4)
  static\img\hub-hp.jpg  карточка HP: скрин Вани из Remastered (inputs\20261121102623_1.jpg — его Lancer + полиция), 21.11;
                как вырезать — outputs\nfs-own-music\dizajn\README.txt (строка hp); то же фото — хаб img\hp.jpg, сайты Unbound / Heat.
  static\img\og.jpg, bg.jpg — полицейский Mustang из UI\MOVIES\275249.VP6 (8 с); исходник превью — outputs\nfs-hp\sajt-dizajn\og.html
  static\img\hub-unbound.jpg, hub-heat.jpg — копии с сайта Heat
  static\favicon.svg     «мигалка» красный | синий
  og.jpg (превью ссылки 1200x630) — ЕЩЕ НЕТ: снять с первого экрана перед публикацией.
