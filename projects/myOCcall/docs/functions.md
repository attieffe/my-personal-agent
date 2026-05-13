# Funzioni principali (sintetico)

## join_call(url)
Apre il link della call nel browser headless OpenClaw. Gestisce login se necessario (con credenziali configurate per piattaforma).

## start_audio_capture(output_file)
Avvia ffmpeg in background, cattura dal monitor PulseAudio (`virtual_out.monitor`) e scrive su file. Supporta chunking temporale per trascrizione progressiva.

## stop_audio_capture()
Termina il processo ffmpeg, restituisce il path del file audio registrato.

## transcribe(audio_file)
Invia il file a Whisper API, restituisce il testo trascritto. Gestisce file grandi dividendoli in chunk da max 25MB.

## summarize(transcript)
Elabora la trascrizione e produce un riassunto strutturato con: partecipanti identificati, punti chiave, decisioni prese, action items.

## full_pipeline(url)
Orchestratore: join → capture → transcribe → summarize. Entry point principale.
