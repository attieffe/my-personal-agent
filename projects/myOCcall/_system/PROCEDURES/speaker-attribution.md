# Procedura: Speaker Attribution via Active Speaker Timeline

> Fonte unica per la strategia di attribuzione parlanti. Descrive l'algoritmo decisionale
> e i selettori DOM piattaforma-specifici. Aggiornare quando i selettori cambiano dopo
> un deploy della piattaforma.

---

## Strategia (v1) — DOM Timeline + Whisper Overlay

La speaker attribution non si basa su diarization vocale pura, ma su una
**timeline active speaker ricavata dal DOM** della piattaforma, poi sovrapposta
ai timestamp della trascrizione Whisper.

Questo approccio è denominato "speaker attribution via active speaker timeline"
(non "speaker diarization") — è più preciso perché sfrutta i segnali della piattaforma
invece di analizzare la voce.

### Pipeline

1. **Durante la call** — `call-monitor.sh` osserva il DOM e salva eventi active speaker
   in `$CALL_DIR/transcripts/speaker-events.jsonl`

2. **Schema evento** (vedi `_system/SCHEMAS/speaker-events-schema.md`):
   ```jsonl
   {"wall_ts": "2026-05-14T14:32:15Z", "call_sec": 125, "speaker_name": "Marco", "event": "speaking_start", "source": "dom_meet", "confidence": 0.9}
   ```

3. **Whisper** produce output JSON per ogni segmento (oltre al `.txt`) — necessario per
   ottenere timestamp per frase/segmento:
   ```bash
   whisper segment.mp3 --output_format verbose_json --output_dir transcripts/
   ```

4. **Normalizzazione timeline** — `call-speaker-overlay.py` genera `transcript-events.jsonl`
   con `call_start_sec`, `call_end_sec`, `text`, `speaker` per ogni intervento

5. **Output finale** — `trascrizione_attribuita.md` con formato:
   ```markdown
   **Marco** [14:32–14:34] Allora vediamo il punto sui carichi...
   **Attilio** [14:35–14:36] Sì, però dobbiamo considerare...
   ```

6. Il file `trascrizione_attribuita.md` alimenta la sezione "Dettaglio per parlante"
   di `SINTESI.md`.

---

## Selettori DOM per piattaforma

I selettori cambiano con ogni deploy della piattaforma. Se un selettore smette di
funzionare, aggiornare la sezione corrispondente in `_knowledge/PLATFORMS.md`.

### Google Meet

```javascript
// Parlante attivo — tile evidenziato (bordo verde)
document.querySelector('[data-participant-id][class*="active"]')
  ?.querySelector('[data-self-name], [aria-label*="nome"]')

// Alternativa — lista partecipanti con stato microfono attivo
document.querySelector('[jscontroller][data-is-muted="false"] [data-participant-id]')
```

### Microsoft Teams

Teams usa attributi `data-tid` pensati per accessibilità e test automatici — i più stabili:

```javascript
// Approccio 1 — roster con stato "speaking"
document.querySelector('[data-tid*="roster"][data-is-speaking="true"] [data-tid*="name"]')

// Approccio 2 — stage/main speaker
document.querySelector('[data-tid="video-tile-display-name-main"]')
document.querySelector('[data-tid="active-speaker-name"]')

// Approccio 3 — aria-label locale italiano
document.querySelector('[aria-label*="sta parlando"]')
  ?.closest('[class*="participant"]')
  ?.querySelector('[class*="name"]')

// Approccio 4 — CSS speaking indicator
document.querySelector('[class*="speaking-indicator--active"]')?.textContent?.trim()
```

### Zoom Web

⚠️ Zoom usa rendering `<canvas>` per i video — i selettori sono meno stabili:

```javascript
// Approccio 1 — tile attivo
document.querySelector('.video-tile--active [class*="display-name"]')
document.querySelector('.active-video .video-avatar__name')

// Approccio 2 — speaker indicator (icona microfono animata)
document.querySelector('[aria-label*="is speaking"]')
  ?.closest('[class*="participant"]')
  ?.querySelector('[class*="display-name"]')

// Approccio 3 — participant list con stato "speaking"
document.querySelector('[class*="participant-item"][class*="speaking"] [class*="display-name"]')
```

> Nota: testare sempre con `page.evaluate()` in devtools durante una call reale
> prima di fissare i selettori Zoom.

---

## Roadmap (v2 e oltre)

- **v2**: Integrare voice fingerprinting per disambiguation quando confidence DOM < 0.5
  (es. parlante non visibile in lista, o DOM non aggiornato)
- **v3**: Combinare DOM timeline + voice features per attribuzione in assenza di segnali DOM
- Database parlanti noti: `_knowledge/SPEAKERS.md` — usato per matching nome → voce

---

## Riferimenti

- Schema eventi: `_system/SCHEMAS/speaker-events-schema.md`
- Script overlay: `_system/scripts/call-speaker-overlay.py`
- Selettori aggiornati e quirk piattaforma: `_knowledge/PLATFORMS.md`
- Parlanti noti: `_knowledge/SPEAKERS.md`
