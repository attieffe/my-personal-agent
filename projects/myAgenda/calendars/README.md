# Calendari — istruzioni

Questa cartella contiene i file `.ics` con gli eventi reali di Atti.

## File attesi

| File | Fonte | Contenuto |
|------|-------|-----------|
| *(da definire)* | *(Atti lo specifica)* | *(es. lavoro Colzani)* |
| *(da definire)* | *(Atti lo specifica)* | *(es. personale/famiglia)* |

## Come esportare da Google Calendar

1. Vai su calendar.google.com → Impostazioni (⚙️)
2. Seleziona il calendario → "Esporta calendario"
3. Scarica il file `.ics`
4. Rinominalo in modo chiaro (es. `lavoro_colzani.ics`, `personale.ics`)
5. Aggiungilo a questa cartella

## Come esportare da Outlook

1. File → Apri ed esporta → Importa/Esporta
2. "Esporta in un file" → "Formato iCalendar (.ics)"
3. Seleziona il calendario → salva

## Frequenza aggiornamento

I file `.ics` sono snapshot statici — si "invecchiano" man mano che nuovi eventi vengono aggiunti.
Aggiornare i file periodicamente (suggerito: settimanale o prima di usare myAgenda per pianificazioni future).

## Note tecniche

- I file `.ics` sono testo plain leggibili direttamente dall'agente
- Gli eventi ricorrenti (RRULE) vengono interpretati come blocchi fissi
- Timezone: l'agente usa sempre Europe/Rome come riferimento
