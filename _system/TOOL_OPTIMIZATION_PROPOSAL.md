# Proposta: Ottimizzazione Token Tools (Deferred Loading Aggressivo)

**Data:** 2026-08-24  
**Autore:** IAcopo  
**Reviewer:** Atti  
**Obiettivo:** Ridurre prompt base da ~26-35k → ~4-10k token (-65-85%)

---

## 🎯 Problema

Ogni sessione carica **15-20k token** solo per definizioni tool, di cui:
- **~8k token (40%)** per tool mai usati in chat Telegram
- **~2k token (10%)** per safety instructions ridondanti
- **~1.5k token (7%)** per esempi verbosi inline

**Impatto:** consumo token inutile, latency più alta, meno spazio per file/conversation.

---

## ✅ Soluzione: Profilo "Coding" (già attivo) + Deny List Tool Pesanti

OpenClaw supporta 4 profili tool:
1. **full** → carica tutto (~40 tool)
2. **coding** → ✅ **ATTUALE** - include: fs, runtime, web, sessions, memory, cron, goals, media (~25 tool)
3. **messaging** → solo message + sessions (~5 tool)
4. **minimal** → ❌ **TROPPO RESTRITTIVO** - solo session_status

**Scoperta:** il profilo "minimal" è inutilizzabile (solo 1 tool), "coding" è già buono.

**Proposta:** mantenere `coding` + aggiungere `message`, `tts`, `nodes` + **bloccare tool pesanti mai usati**.

---

## 🔧 Configurazione Proposta

### File: `~/.openclaw/openclaw.json`

**Sezione `tools` (riga 231):**

```json5
{
  "tools": {
    // ✅ MANTENIAMO: "coding" (già include fs, runtime, web, sessions, memory, cron)
    "profile": "coding",
    
    // ➕ Aggiungiamo tool messaging/nodes mancanti ma necessari
    "alsoAllow": [
      "message",   // Telegram/WhatsApp messaging (NON in coding, necessario!)
      "tts",       // Voice notes (già in coding come group:media)
      "nodes"      // Foto/screenshot Android (NON in coding, occasionale)
    ],
    
    // ❌ BLOCCHIAMO tool pesanti MAI usati in chat Telegram
    "deny": [
      "google_meet",        // ~1.500 token - mai usato
      "browser",            // ~2.500 token - mai usato  
      "canvas",             // ~300 token - mai usato
      "image_generate",     // ~600 token - generazione immagini AI
      "music_generate",     // ~400 token - mai usato
      "video_generate",     // ~600 token - mai usato
      "gateway",            // ~500 token - config changes (raro)
      "skill_workshop"      // ~800 token - gestione skills (raro)
    ],
    
    "web": {
      "search": {
        "provider": "duckduckgo",
        "enabled": true
      }
    },
    "sessions": {
      "visibility": "all"
    }
  }
}
```

---

## 📊 Stima Risparmio Token

### Prima (profile: "coding" ATTUALE - senza deny)
| Categoria | Tool Count | Token Totali |
|-----------|-----------|--------------|
| Coding profile | ~25 | ~12.000-15.000 |
| Deferred (Colzani, etc.) | ~30 | ~500 |
| Messaging (mancante) | ~1 | ~3.500 |
| **TOTALE** | **~56** | **~16.000-19.000** |

### Dopo (profile: "coding" + alsoAllow + deny)
| Categoria | Tool Count | Token Totali |
|-----------|-----------|--------------|
| Coding profile | ~25 | ~12.000-15.000 |
| alsoAllow (message, nodes) | ~2 | ~4.000 |
| Deferred (Colzani, etc.) | ~30 | ~500 |
| ❌ Denied (blocked, 0 token) | ~8 | **0** |
| **TOTALE** | **~57** | **~16.500** |

**⚠️ PROBLEMA:** Il blocco con `deny` **non riduce token** se i tool sono già "always loaded"!

**💡 SOLUZIONE VERA:** bisogna che OpenClaw supporti **deferred loading** per i tool denied, non solo bloccarli.

**Risparmio stimato con deny:** ~5.900 token (-30%) SE i tool denied diventano deferred  
**Risparmio stimato senza deferred:** ~0 token (i tool restano nel prompt ma bloccati)

---

## 🔍 Verifica Pre-Implementazione

### ✅ Risposte alle Domande:

1. **✅ RISOLTO: Il profilo "coding" include già tutto il necessario**
   - Bash/Read/Write/Edit/Grep/Glob → ✅ in `group:fs` + `group:runtime`
   - web_search/web_fetch → ✅ in `group:web`
   - memory_search/memory_get → ✅ in `group:memory`
   - sessions_*, cron → ✅ inclusi

2. **❌ PROBLEMA CRITICO: `deny` NON rende i tool "deferred"**
   - I tool bloccati con `deny` restano nel prompt (sempre loaded)
   - Vengono solo BLOCCATI all'uso, ma occupano token
   - **NON c'è risparmio token** con `deny` alone!

3. **⚠️ OpenClaw NON supporta deferred loading configurabile per tool nativi**
   - Solo tool MCP/Colzani sono deferred
   - Tool nativi (message, browser, google_meet) sono sempre "always loaded"
   - **La config `deny` è solo security policy, NON ottimizzazione token**

### 🔴 Conclusione Critica

**Il meccanismo "deferred loading" che cercavamo NON ESISTE per tool nativi OpenClaw.**

I tool vengono caricati così:
- **Always loaded:** tutti i tool del profilo + alsoAllow (occupano token)
- **Deferred:** solo MCP servers e plugin esterni (lista nomi, ~20 token/tool)

**Non possiamo** rendere `browser`, `google_meet`, `video_generate` deferred con la config attuale.

---

## 🧪 Test Plan

1. **Backup config attuale:**
   ```bash
   cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup-20260824
   ```

2. **Applica modifiche** (vedi sezione "Configurazione Proposta")

3. **Restart OpenClaw Gateway:**
   ```bash
   openclaw daemon restart
   ```

4. **Test funzionalità critiche:**
   - ✅ Leggi/scrivi file (Read/Write/Edit)
   - ✅ Invia messaggio Telegram (message)
   - ✅ Recall memoria (memory_search)
   - ✅ Web search (web_search)
   - ✅ Check cron jobs (cron)

5. **Verifica token prompt:**
   - Chiedi "dimmi il peso prompt" e confronta con baseline (~26-35k)
   - Target: <10k token base

6. **Test tool deferred:**
   - Prova a chiamare un tool non in `alsoAllow` (es. google_meet)
   - Deve funzionare via `ToolSearch` on-demand

---

## ⚠️ Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Tool essenziali mancanti in "minimal" | Media | Alto | Backup config + test immediato |
| Tool deferred non funzionano | Bassa | Medio | Aggiungere in `alsoAllow` temporaneamente |
| Profilo minimal troppo restrittivo | Media | Basso | Passare a "coding" + deny list |
| Break workflow esistenti | Bassa | Alto | Rollback immediato se problemi |

**Rollback plan:**
```bash
cp ~/.openclaw/openclaw.json.backup-20260824 ~/.openclaw/openclaw.json
openclaw daemon restart
```

---

## 📝 Checklist Approvazione

- [ ] **Atti:** Revisione proposta e domande
- [ ] **IAcopo:** Risposta a domande aperte (cosa include "minimal"?)
- [ ] **Atti:** Approvazione finale
- [ ] **IAcopo:** Implementazione + test
- [ ] **IAcopo:** Verifica risparmio token effettivo
- [ ] **IAcopo:** Documentazione finale in `_system/TOOL_OPTIMIZATION.md`

---

## 🚀 Next Steps

1. **Verifica schema "minimal"** - cosa include esattamente?
2. **Atti approva/modifica** la lista `alsoAllow`
3. **Test su workspace separato** (opzionale: `openclaw --profile test`)
4. **Deploy in produzione** se test OK

---

## 💡 Soluzioni Alternative (VERE)

### A) ❌ Config `deny` - NON FUNZIONA
- Blocca i tool ma **NON riduce token**
- Solo security policy, non ottimizzazione
- **SCARTATA**

### B) ⚠️ Profilo "messaging" invece di "coding"
- Include: solo `message` + `sessions_*` + `session_status`
- PRO: Molto leggero (~5k token)
- CONTRO: Mancano file operations (Read/Write/Edit/Bash) - **inutilizzabile**
- **SCARTATA**

### C) ✅ Feature Request a OpenClaw: Deferred Loading Configurabile
- Proporre meccanismo per rendere tool nativi deferred
- Schema: `tools.deferred: ["browser", "google_meet", ...]`
- Beneficio: -80% token per tool non usati
- **RACCOMANDATO** come soluzione a lungo termine

### D) ✅ Workaround: Claude Code Settings (client-side)
- Se Claude Code supporta tool filtering client-side
- File `.claude/settings.json` con lista tool permitted
- Verificare se riduce prompt o solo blocca uso
- **DA VERIFICARE**

### E) 🔧 Hack: Custom MCP Wrapper
- Wrappare tool nativi come MCP server
- Far diventare deferred forzatamente
- PRO: Funziona ora
- CONTRO: Manutenzione custom, rischio break
- **ULTIMA RISORSA**

**Raccomandazione:** Opzione C (feature request) + documentare limitazione attuale.

---

**Pronto per revisione.** Dimmi se approvi, modifichi o preferisci una delle alternative.
