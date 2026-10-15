# Software utili

Strumenti software per la produzione video del canale.
Legenda: 🧑 = indicazione di Atti · 🤖 = proposta/ricerca IAcopo.

---

## Editing video

- 🧑 Da valutare tra **CapCut** e **DaVinci Resolve** — obiettivo: compromesso giusto tra funzionalità e difficoltà per chi già sa editare.
- 🤖 **Consiglio: DaVinci Resolve (versione free)** come editor principale:
  - versione gratuita tra le più complete in assoluto (color grading, Fusion per motion graphics, Fairlight per audio) — profilo da "crescita" senza costi;
  - nessun watermark, niente abbonamento (Studio è acquisto una sola volta, solo se serve);
  - curva di aprendizaje moderata per chi ha già esperienza di editing: la timeline è classica, le funzioni avanzate si assorbono col tempo.
- 🤖 **CapCut** ha senso come secondario: velocissimo per Shorts/verticali con template e sottotitoli auto — ma sempre più funzioni dietro abbonamento Pro e tetto qualitativo più basso.

## Automazioni / pipeline (CLI)

- 🧑 **ffmpeg** — automatismi vari: intro fisse precompilate, richiamo di moduli, batch processing.
- 🤖 (nota) si integra bene con Auto-Editor e Remotion per una pipeline semi-automatica raw → cut → export.

## Rimozione silenzi / spazi vuoti

- 🤖 **Auto-Editor** — quello che cercavi 🎯
  - open source, da riga di comando: analizza il volume e taglia automaticamente i silenzi;
  - parametri regolabili (soglia, margini di silenzio da tenere);
  - esporta anche timeline per DaVinci Resolve / Premiere → il primo cut lo fa lui, poi rifinisci a mano;
  - pagina: github.com/WyattBlue/auto-editor

## Infografiche animate da inserire nei video

- 🤖 **Jitter** (jitter.video) — template di grafici/infografiche animati, si usa da browser, esporta video da incollare in montaggio. L'opzione "veloce e bella".
- 🤖 **Remotion** (remotion.dev) — video programmatici in React: perfetto per un profilo tecnico, template riutilizzabili via codice (es. schermate statistiche generate automaticamente). Gratis per uso individuale.
- 🤖 **Flourish** (flourish.studio) — il classico per i grafici animati tipo bar chart race che si vedono nei video YouTube di dati.

---

Vedi anche: [[montaggio]] · [[strumentazione]]
