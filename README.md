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


### Dodatocne informacie

Na GitHube je nakonfigurovany workflow (teda pipeline), ktora nahodi ubuntu snapshot s pripravenym python prostredim. Nasledne si doinstaluje potrebne kniznice definovane v subore `requirements.txt`.

Script `extrakcia_dat.py` sa pusta denne o 07:00 v takto pripravenom prostredi a jeho vysledkom je artifact, ktory obsahuje dva vystupne subory (CSV a JSONL) s extrahovanymi datami. Tento artifact je dostupny na GitHube v sekcii Actions pod poslednym behom workflow.