# Appunti Operativi

## Decisioni prese

- **Naming:** `YYYYMMDD titolo.ext` — data estratta dal documento, non dalla ricezione
- **Mai cancellare:** i file originali finiscono in `90_processed/` dopo l'archiviazione
- **Conferma sempre:** nessuna copia su Drive senza ok di Atti
- **Cartella input/:** gitignored — il contenuto non va in repository
- **Drive access:** rclone CLI con remote `gdrive` (token in `~/.config/rclone/rclone.conf`)

## Canale Telegram intake

- chat_id: -1003877516285
- topic_id: 2069
- Nome: "Archiviazione documenti"

## Path Drive

rclone usa il prefisso `gdrive:` che corrisponde alla radice di "Il mio Drive".

Quindi:
- `Il mio Drive\Atti\Documenti\...` → `gdrive:Atti/Documenti/...`
- `Il mio Drive\Ingenio\...` → `gdrive:Ingenio/...`
