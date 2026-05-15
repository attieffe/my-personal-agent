# Schema: Speaker Events (JSONL)

> Formato del file `transcripts/speaker-events.jsonl` generato durante la call
> da `call-monitor.sh` tramite polling DOM della piattaforma.

## Campi obbligatori

| Campo | Tipo | Descrizione |
|---|---|---|
| `wall_ts` | string (ISO 8601) | Timestamp wall-clock dell'evento |
| `call_sec` | number | Secondi dall'inizio della call (da bot_join_epoch_ms) |
| `speaker_name` | string | Nome visualizzato dalla piattaforma |
| `event` | enum | `speaking_start` \| `speaking_end` \| `joined` \| `left` |
| `source` | string | Selettore/metodo usato: `dom_meet`, `dom_teams`, `dom_zoom` |
| `confidence` | number (0.0–1.0) | Affidabilità del rilevamento (1.0 = certezza) |

## Campi opzionali

| Campo | Tipo | Descrizione |
|---|---|---|
| `selector_used` | string | Selettore CSS/XPath effettivamente matchato |
| `raw_text` | string | Testo grezzo del nodo DOM (per debug) |

## Esempio

```jsonl
{"wall_ts":"2026-05-14T14:08:12Z","call_sec":0,"speaker_name":"Attilio F.","event":"joined","source":"dom_teams","confidence":1.0}
{"wall_ts":"2026-05-14T14:08:45Z","call_sec":33,"speaker_name":"Marco","event":"joined","source":"dom_teams","confidence":1.0}
{"wall_ts":"2026-05-14T14:09:02Z","call_sec":50,"speaker_name":"Marco","event":"speaking_start","source":"dom_teams","confidence":0.9,"selector_used":"[data-tid*=\"roster\"][data-is-speaking=\"true\"]"}
{"wall_ts":"2026-05-14T14:09:15Z","call_sec":63,"speaker_name":"Marco","event":"speaking_end","source":"dom_teams","confidence":0.9}
{"wall_ts":"2026-05-14T14:09:16Z","call_sec":64,"speaker_name":"Attilio F.","event":"speaking_start","source":"dom_teams","confidence":0.85}
```

## Note

- Il file viene creato vuoto al join e popolato in append durante la call
- Gli eventi `joined`/`left` sono supplementari — la fonte primaria partecipanti è META.md
- Per l'algoritmo di overlay, vedi `_system/PROCEDURES/speaker-attribution.md`
