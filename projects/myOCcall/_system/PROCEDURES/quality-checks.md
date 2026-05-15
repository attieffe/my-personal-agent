# Procedura: Quality Checks — Audio e Trascrizione

> Controlli da eseguire post-call prima di generare la SINTESI.md finale.
> Se un check fallisce, loggare l'anomalia e notificare Atti.

---

## Check 1 — Audio non silenzioso

```bash
ffmpeg -i "$CALL_DIR/audio/segments/segment-0000.mp3" \
  -filter:a volumedetect -f null /dev/null 2>&1 | grep max_volume

# PASS:  max_volume > -40 dB  (audio reale presente)
# FAIL:  max_volume < -80 dB  (silenzio — routing audio non configurato)
```

Se tutti i segmenti sono `silent`: verificare routing audio (`_system/PROCEDURES/audio-capture.md`).

---

## Check 2 — Segmenti validi nel manifest

```bash
# Contare segmenti validi vs totali
grep -c "^valid" "$CALL_DIR/audio/manifest.tsv"     # attesi > 0
grep -c "^silent" "$CALL_DIR/audio/manifest.tsv"    # devono essere < totale
```

Vedi `_system/PROCEDURA_AUDIO_TRASCRIZIONE.md` per il formato manifest.

---

## Check 3 — Trascrizione non vuota o ripetitiva

```bash
# Minimo 10 parole
wc -w "$CALL_DIR/trascrizione.txt"

# Nessun boilerplate Whisper
grep -i "sottotitoli creati dalla comunità" "$CALL_DIR/trascrizione.txt" && echo "BOILERPLATE DETECTED"

# Nessun loop ripetitivo (stesso testo per > 5 righe consecutive)
# Controllo manuale o script dedicato
```

---

## Check 4 — Durata call vs durata audio

```bash
# Durata totale audio registrato
grep "duration_sec" "$CALL_DIR/audio/manifest.tsv" | awk -F'\t' '{sum+=$3} END {print sum/60 " min"}'

# Durata attesa dalla call (da META.md: bot_leave - bot_join)
# Warning se differenza > 10 minuti
```

---

## Check 5 — META.md compilato

Verificare che META.md contenga almeno:
- [ ] `platform`
- [ ] `url`
- [ ] `bot_join` (timestamp)
- [ ] `bot_leave` (timestamp)
- [ ] Almeno 1 partecipante noto

---

## Azioni in caso di fallimento

| Check fallito | Azione |
|---|---|
| Audio silenzioso | Notificare Atti, NON generare SINTESI, loggare in `_knowledge/WORKAROUNDS.md` |
| 0 segmenti validi | Come sopra |
| Trascrizione < 10 parole | Notificare Atti con warning, generare SINTESI vuota con nota |
| Boilerplate detected | Rimuovere righe boilerplate, procedere |
| Durata mismatch > 10min | Warning nella SINTESI, non bloccare |
| META.md incompleto | Compilare i campi mancanti prima di procedere |
