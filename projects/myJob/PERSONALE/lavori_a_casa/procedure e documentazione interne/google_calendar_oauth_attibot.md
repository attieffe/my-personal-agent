# Google Calendar OAuth — AttiBot (myAgenda OC)

**Data setup:** 2026-05-18
**Scopo:** Permettere ad AttiBot di scrivere eventi sul calendario "myAgenda OC"

---

## Architettura

| Elemento | Valore |
|---|---|
| Calendario | myAgenda OC |
| Proprietario | `ing.fiumano@gmail.com` |
| Account delegato | `myjob@ingeniosolution.it` |
| Scope OAuth | `https://www.googleapis.com/auth/calendar` |
| Credenziali | `projects/myAgenda/_credentials/` |

---

## Come funziona

1. Il calendario "myAgenda OC" è creato su `ing.fiumano@gmail.com`
2. `ing.fiumano@gmail.com` lo ha condiviso con `myjob@ingeniosolution.it` con permesso **"make changes and manage sharing"**
3. `myjob@ingeniosolution.it` ha accettato l'invito tramite il link ricevuto via email (necessario una sola volta)
4. Il token OAuth (`google_token.json`) è emesso per `myjob@ingeniosolution.it` e usa il `client_id` della Google Cloud app creata su `ing.fiumano@gmail.com`
5. Il `refresh_token` si rinnova automaticamente — non serve re-autorizzare

---

## File rilevanti

```
projects/myAgenda/_credentials/
├── google_token.json     ← token attivo (access + refresh)
├── oauth_client.json     ← client_id e client_secret dell'app Google Cloud
└── oauth_flow.py         ← script per ri-autorizzare (solo se il refresh_token scade)
```

---

## Procedura di ri-autorizzazione (solo se necessario)

Il refresh_token scade solo se:
- L'app Google Cloud viene revocata
- Il token viene revocato manualmente da Google Account

In quel caso:
1. Eseguire `oauth_flow.py` da terminale
2. Aprire l'URL nel browser **loggato come `myjob@ingeniosolution.it`**
3. Autorizzare e incollare il codice
4. Il nuovo token viene salvato automaticamente in `google_token.json`

---

## Troubleshooting

| Errore | Causa | Soluzione |
|---|---|---|
| `404 Not Found` sul calendario | `myjob` non ha accettato l'invito | Cliccare link nell'email di invito da `ing.fiumano@gmail.com` |
| `401 Unauthorized` | Access token scaduto | Il sistema fa refresh automatico; se fallisce, ri-autorizzare |
| Calendario non in calendarList | Invito non accettato | Stesso punto del 404 sopra |

---

## Note operative

- Il `calendar_id` corretto è salvato in `google_token.json` come campo `calendar_id`
- AttiBot usa queste credenziali per inserire eventi da reminder padel e altri automatismi
- Il token non ha scope per leggere email o altri servizi Google — solo Calendar
