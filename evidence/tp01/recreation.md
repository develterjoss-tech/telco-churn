# Recréation de l'environnement (TP01, section 4)

## Procédure
1. Environnement d'origine : `.venv`, créé par `uv add pandas`.
2. Mise de côté : `mv .venv venv.bak` (dossier ignoré par Git).
3. Recréation depuis `pyproject.toml` et `uv.lock` : `uv sync --locked` (nouveau `.venv`, aucune re-résolution).
4. Même script, même CSV, lancé dans chacun des deux environnements :
   - ancien : `venv.bak/bin/python scripts/inspect_data.py` -> `data_overview_before.json`
   - recréé : `uv run python scripts/inspect_data.py` -> `data_overview_after.json`
5. Liste des paquets de chaque environnement : `uv pip list --python <python de l'env>` -> `env_before.txt`, `env_after.txt`.

## Résultat
- Rapports identiques (`diff` vide) : mêmes dimensions, cible, doublons, manquants et SHA-256 source.
- Environnements identiques : Python 3.12.13, pandas 3.1.0, numpy 2.5.4, mêmes paquets.
- Détail dans `comparison.txt`.

## Limites
- Les preuves "before" ont été capturées depuis `venv.bak` **après** le déplacement, pas avant : elles montrent l'état de l'ancien environnement conservé tel quel.
- Le lockfile fixe les versions des paquets, pas le matériel ni le système d'exploitation.
- Le chemin local du paquet éditable (`telco-churn`) a été retiré des listes de paquets (`sed`), pour ne pas publier l'arborescence de la machine.
