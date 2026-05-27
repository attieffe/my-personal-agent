Documento tecnico ricevuto

### Funzione `cm_redirect_users_by_role` - Gestione Redirect Utenti

- `file`: `wp-content/themes/blancone/functions.php`
- `hook`: `admin_init`
- `condizione`: attiva solo se non è una chiamata AJAX

#### Scenario 1 - utente con un solo ruolo

- `centro_autorizzato` → `/dashboard/`
- `paziente_centro` → `/area-riservata-ai-pazienti/`
- `consulente_capoarea` → `/piattaforma-consulenti/`
- `consulente_agente` → `/piattaforma-consulenti/`
- `piattaforma_agenti_IDS` → `/piattaforma-consulenti/`
- altri ruoli → nessun redirect, accesso admin normale

#### Scenario 2 - utente con ruoli multipli

- Se l'utente non è `administrator`, `ids_dental` o `promo_click`, la priorità è:
  - `paziente_centro` → `/area-riservata-ai-pazienti/`
  - `centro_autorizzato` → `/dashboard/`
  - `consulente_capoarea` / `consulente_agente` / `piattaforma_agenti_IDS` → `/piattaforma-consulenti/`
  - nessuno dei precedenti → homepage `/`

#### Eccezioni che possono accedere all'admin

- `administrator`
- `ids_dental`
- `promo_click`

#### Note tecniche

- la priorità viene valutata dall'alto verso il basso
- ogni redirect termina con `exit()`
- la funzione non si attiva durante chiamate AJAX per evitare conflitti
- sul dominio `blancone.eu` esistono anche redirect dichiarati nel tema `blancone_new`, file `wp-content/themes/blancone_new/inc/bitdesign-functions.php`

#### Data documentazione

- `26 maggio 2026`
