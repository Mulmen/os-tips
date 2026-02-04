# OS-tips (Streamlit) – utan secrets

## Kör lokalt
```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub + Streamlit Cloud
- Lägg upp allt i ett GitHub-repo.
- Deploy i Streamlit Community Cloud: välj repo + `app.py`.

## Viktigt om persistens
Denna version sparar lokalt i:
- `data/picks.json`
- `data/results.csv`

På Streamlit Cloud kan filer ibland nollställas vid omstart/redeploy.
Använd fliken **Backup / Restore** för att ladda ner och återställa.

## Datafiler
- `data/athletes.csv` (athlete_id,name,sport)
- `data/results.csv` (athlete_id,medal) medal: None/Bronze/Silver/Gold
