# Calendari — fonti live e calendario proposte

## Fonti live (da recuperare sempre via curl, mai scaricare)

| Nome | URL | Contenuto |
|------|-----|-----------|
| Colzani (Outlook) | `https://outlook.office365.com/owa/calendar/7fb3457027034844b5d50b48e2bec69c@gruppocolzani.it/f25283ccce134adabf48798ad0fffa6915049710397185913243/S-1-8-3933509339-3548900094-466301827-3675311127/reachcalendar.ics` | Calendario lavoro Colzani |
| Personale Gmail | `https://calendar.google.com/calendar/ical/ing.fiumano%40gmail.com/private-1e6a7d3bbd7c548786476f11207ad71f/basic.ics` | Tutti gli impegni personali di Atti |
| Padel Playtomic | `https://ingsoftware.it/ingsoftware/playtomic-ical/ical.php?auth=5uof_dBSABKnWtNZdQP9nm4yOkmlEM8gkCTRAsYS7ZT3lYqu__uuQiB22Sd5JJvBbdlqaP-9AsjcP0LpKdVgS5VGbCwtu19wQrA&asd=1` | Partite padel prenotate su Playtomic |

**Regola:** usare sempre il link live via `curl -L "<URL>"`. Non salvare mai i dati come file statico — diventano subito obsoleti.

**Regola padel:** le partite di padel vanno cercate in **entrambe** le fonti:
- Playtomic ICS → prenotazioni fatte tramite app
- Personale Gmail ICS → eventi con "padel" nel titolo (allenamenti, tornei, partite fuori Playtomic)

Unire sempre i risultati di entrambe le fonti prima di mostrare le partite.

## Conversione timezone — OBBLIGATORIA

Gli ICS di Google Calendar e Outlook esportano i tempi in **UTC** (senza suffisso `Z` ma comunque UTC).
Gli ICS di Playtomic usano il suffisso `Z` esplicito (anch'essi UTC).

**Regola ferrea: convertire SEMPRE in ora italiana (Europe/Rome) prima di mostrare qualsiasi orario ad Atti.**

- Estate (CEST, fine marzo–fine ottobre): UTC + 2h
- Inverno (CET, fine ottobre–fine marzo): UTC + 1h

❌ MAI mostrare orari UTC nudi — causano confusione e decisioni sbagliate.
✅ SEMPRE mostrare in ora locale italiana, es. "20:00" non "18:00Z".

## Calendario proposte — myAgenda OC

Calendario Google su cui l'agente può **scrivere** tramite Google Calendar API (OAuth già autorizzato).

- **Calendar ID:** `07a5eeed6b895609bd39fd70336815e5c4f81f59ab79527c21677fcfcb548108@group.calendar.google.com`
- **Credenziali:** `_credentials/google_token.json` (access token + refresh token + client_id/secret)
- **Scope:** `https://www.googleapis.com/auth/calendar`

Per inserire un evento: `POST https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events` con Bearer token.
Se il token è scaduto, rinnovarlo con il refresh_token via `https://oauth2.googleapis.com/token`.
