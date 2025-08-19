### Spustenie

1. Nainstalujte potrebne kniznice:
    ```bash
    pip install -r requirements.txt
    ```

2. Nastavte si environmentalu premennu `GOLEMIO_API_KEY` s vasim API klucom. Pripadne ju mozete priamo vlozit do skriptu na riadok 120.

3. Script je mozne spustit s troma parametrami:
    - `-o` alebo `--out-prefix`: prefix pre vystupne subory (CSV a JSONL)
    - `--page-size`: velkost stranky pre API dotazy
    - `--verbose`: zapne podrobne logovanie

4. Spustite skript:
    ```bash
    python extrakcia_dat.py -o vystup_kniznice
    ```