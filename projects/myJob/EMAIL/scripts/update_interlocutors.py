#!/usr/bin/env python3
"""
update_interlocutors.py - Auto-aggiornamento database interlocutori

Aggiorna INTERLOCUTORS.md quando Attilio conferma una nuova categorizzazione.
Richiede conferma esplicita prima di modificare il file.

Ambiente: Ubuntu 24.00 / openclaw
Python: 3.x
Encoding: UTF-8
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List


class InterlocutorsUpdater:
    """Gestisce aggiornamenti a INTERLOCUTORS.md con conferma."""
    
    def __init__(self, email_root: str):
        """
        Args:
            email_root: Path assoluto alla cartella EMAIL
        """
        self.email_root = Path(email_root)
        self.interlocutors_file = self.email_root / "INTERLOCUTORS.md"
        self.changelog_file = self.email_root / "CHANGELOG.md"
        
    def propose_new_sender(self, sender_data: Dict) -> Dict:
        """
        Propone aggiunta di nuovo mittente a INTERLOCUTORS.md.
        
        Args:
            sender_data: Dict con chiavi:
                - email: indirizzo email
                - name: nome persona
                - role: ruolo (es. "sviluppatore", "consulente AS400")
                - society: società di appartenenza
                - area: area pertinenza (COLZANI, DIRETTI, ecc.)
                - topics: lista argomenti tipici
                - todo_files: lista file TODO associati
                - notes: note aggiuntive
                
        Returns:
            Dict con proposta formattata e flag requires_confirmation
        """
        proposal = {
            'action': 'add_new_sender',
            'requires_confirmation': True,
            'sender_data': sender_data,
            'markdown_entry': self._format_sender_entry(sender_data),
            'message': self._format_proposal_message(sender_data)
        }
        
        return proposal
    
    def propose_update_sender(
        self,
        email: str,
        updates: Dict
    ) -> Dict:
        """
        Propone aggiornamento di mittente esistente.
        
        Args:
            email: email del mittente da aggiornare
            updates: dict con campi da aggiornare
            
        Returns:
            Dict con proposta formattata
        """
        proposal = {
            'action': 'update_sender',
            'requires_confirmation': True,
            'email': email,
            'updates': updates,
            'message': f"Aggiornare informazioni per {email}:\n"
        }
        
        for key, value in updates.items():
            proposal['message'] += f"  - {key}: {value}\n"
        
        return proposal
    
    def apply_update(
        self,
        proposal: Dict,
        confirmed: bool = False
    ) -> bool:
        """
        Applica aggiornamento se confermato.
        
        Args:
            proposal: proposta generata da propose_*
            confirmed: True se Attilio ha confermato
            
        Returns:
            True se aggiornamento applicato, False altrimenti
        """
        if not confirmed:
            print("⚠️  Aggiornamento NON confermato - nessuna modifica")
            return False
        
        if proposal['action'] == 'add_new_sender':
            return self._add_sender(proposal['sender_data'])
        elif proposal['action'] == 'update_sender':
            return self._update_sender(proposal['email'], proposal['updates'])
        
        return False
    
    def _format_sender_entry(self, sender_data: Dict) -> str:
        """Formatta entry markdown per nuovo mittente."""
        name = sender_data.get('name', 'Unknown')
        email = sender_data.get('email', '')
        role = sender_data.get('role', '(da catalogare)')
        society = sender_data.get('society', '(da catalogare)')
        area = sender_data.get('area', 'EMAIL')
        topics = sender_data.get('topics', [])
        todo_files = sender_data.get('todo_files', [])
        notes = sender_data.get('notes', '')
        
        entry = f"""
### {name}
- **Email**: {email}
- **Ruolo**: {role}
- **Società**: {society}
- **Area pertinenza**: {area}
- **Argomenti tipici**:
"""
        
        if topics:
            for topic in topics:
                entry += f"  - {topic}\n"
        else:
            entry += "  - (da catalogare)\n"
        
        if todo_files:
            entry += f"- **File TODO associati**: {', '.join(f'`{f}`' for f in todo_files)}\n"
        else:
            entry += "- **File TODO associati**: (nessuno al momento)\n"
        
        if notes:
            entry += f"- **Note**: {notes}\n"
        
        return entry
    
    def _format_proposal_message(self, sender_data: Dict) -> str:
        """Formatta messaggio proposta per Telegram (user-friendly)."""
        name = sender_data.get('name', 'Unknown')
        email = sender_data.get('email', '')
        role = sender_data.get('role', 'ruolo sconosciuto')
        society = sender_data.get('society', 'società sconosciuta')
        
        msg = f"""
🆕 **Nuovo mittente da aggiungere al database**

**Nome**: {name}
**Email**: {email}
**Ruolo**: {role}
**Società**: {society}

Vuoi che aggiunga questa persona al database degli interlocutori abituali?
Così la prossima volta che arriva una sua email, la riconoscerò automaticamente.

✅ Conferma | ❌ Ignora | 📝 Modifica dettagli
"""
        return msg.strip()
    
    def _add_sender(self, sender_data: Dict) -> bool:
        """Aggiunge nuovo mittente a INTERLOCUTORS.md."""
        try:
            # Leggi file esistente
            with open(self.interlocutors_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determina sezione corretta (Interni, Esterni, Fornitori)
            society = sender_data.get('society', '')
            if 'colzani' in society.lower() or 'gruppo' in society.lower():
                section_marker = "## Mittenti Interni (Gruppo Colzani)"
            elif sender_data.get('role', '').lower().startswith('consulente'):
                section_marker = "## Consulenti Esterni"
            else:
                section_marker = "## Fornitori / Partner"
            
            # Trova posizione di inserimento
            entry = self._format_sender_entry(sender_data)
            
            # Inserisci dopo il marker della sezione
            if section_marker in content:
                parts = content.split(section_marker, 1)
                # Trova la prossima sezione (inizia con ##)
                after_section = parts[1]
                next_section_match = re.search(r'\n##\s+', after_section)
                
                if next_section_match:
                    # Inserisci prima della prossima sezione
                    insert_pos = next_section_match.start()
                    new_content = (
                        parts[0] + section_marker +
                        after_section[:insert_pos] + entry + "\n" +
                        after_section[insert_pos:]
                    )
                else:
                    # Aggiungi alla fine della sezione
                    new_content = parts[0] + section_marker + after_section + entry + "\n"
            else:
                # Sezione non trovata, aggiungi alla fine
                new_content = content + "\n" + entry
            
            # Backup del file originale
            backup_file = self.interlocutors_file.with_suffix('.md.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Scrivi nuovo contenuto
            with open(self.interlocutors_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Log in changelog
            self._log_change(
                f"Aggiunto nuovo mittente: {sender_data.get('name')} ({sender_data.get('email')})"
            )
            
            print(f"✅ Mittente {sender_data.get('name')} aggiunto a INTERLOCUTORS.md")
            return True
            
        except Exception as e:
            print(f"❌ Errore aggiungendo mittente: {e}")
            return False
    
    def _update_sender(self, email: str, updates: Dict) -> bool:
        """Aggiorna mittente esistente."""
        # TODO: Implementare update di entry esistente
        # Per ora solo placeholder
        print(f"⚠️  Update sender non ancora implementato: {email}")
        return False
    
    def _log_change(self, message: str):
        """Aggiunge entry a CHANGELOG.md."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            log_entry = f"**{timestamp}** | **Auto-update**: {message}\n"
            
            if self.changelog_file.exists():
                with open(self.changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Inserisci all'inizio (dopo header se presente)
                if content.startswith('#'):
                    lines = content.split('\n')
                    header_end = 1
                    for i, line in enumerate(lines):
                        if i > 0 and not line.startswith('#'):
                            header_end = i
                            break
                    new_content = '\n'.join(lines[:header_end]) + '\n\n' + log_entry + '\n'.join(lines[header_end:])
                else:
                    new_content = log_entry + content
            else:
                new_content = f"# CHANGELOG - EMAIL\n\n{log_entry}"
            
            with open(self.changelog_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            print(f"⚠️  Errore logging change: {e}")


def main():
    """Esempio di utilizzo standalone."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python update_interlocutors.py <email_root> [sender_json]")
        sys.exit(1)
    
    email_root = sys.argv[1]
    
    # Sender di esempio
    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            sender_data = json.load(f)
    else:
        sender_data = {
            'email': 'test@example.com',
            'name': 'Mario Rossi',
            'role': 'Consulente tecnico',
            'society': 'Partner Esterno',
            'area': 'COLZANI',
            'topics': ['Infrastruttura', 'Cloud'],
            'todo_files': [],
            'notes': 'Test entry'
        }
    
    updater = InterlocutorsUpdater(email_root)
    
    # Genera proposta
    print("📝 Generazione proposta...")
    proposal = updater.propose_new_sender(sender_data)
    
    print("\n" + proposal['message'])
    print("\n" + "="*60)
    print("Entry markdown che verrà aggiunta:")
    print("="*60)
    print(proposal['markdown_entry'])
    
    # Simulazione conferma (in produzione arriva da Telegram)
    confirm = input("\n\nConfermi aggiunta? (y/n): ").strip().lower() == 'y'
    
    if confirm:
        success = updater.apply_update(proposal, confirmed=True)
        if success:
            print("\n✅ Aggiornamento completato!")
        else:
            print("\n❌ Aggiornamento fallito")
    else:
        print("\n⚠️  Aggiornamento annullato")


if __name__ == '__main__':
    main()
