#!/usr/bin/env python3
"""
match_todos.py - Match email con TODO esistenti

Cerca nei file TODO dell'area pertinente per identificare task correlati
all'email ricevuta, evitando di creare duplicati.

Ambiente: Ubuntu 24.00 / openclaw
Python: 3.x
Encoding: UTF-8
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class TodoMatcher:
    """Match email con TODO esistenti basato su vari criteri."""
    
    def __init__(self, workspace_root: str):
        """
        Args:
            workspace_root: Path assoluto alla root del workspace myJob
        """
        self.workspace_root = Path(workspace_root)
        self.colzani_path = self.workspace_root / "COLZANI"
        self.diretti_path = self.workspace_root / "DIRETTI"
        
    def find_todos_in_area(self, area: str, society: Optional[str] = None) -> List[Dict]:
        """
        Trova tutti i TODO nell'area specificata.
        
        Args:
            area: Area di pertinenza (COLZANI, DIRETTI, GET_ME_DIGITAL, ecc.)
            society: Società specifica (es. SPORTIT SRL) se area è COLZANI
            
        Returns:
            Lista di dict con: {file, line, text, context}
        """
        todos = []
        
        if area == "COLZANI":
            # Cerca in COLZANI/TEAM, COLZANI/CONSULENTI, ecc.
            search_paths = [
                self.colzani_path / "TODO.md",
                self.colzani_path / "TEAM" / "Fabio_TODO.md",
                self.colzani_path / "TEAM" / "Alessandro_TODO.md",
                self.colzani_path / "TEAM" / "README.md",
                self.colzani_path / "CONSULENTI" / "README.md",
                self.colzani_path / "README.md",
            ]
            
            for path in search_paths:
                if path.exists():
                    todos.extend(self._extract_todos_from_file(path))
                    
        elif area == "DIRETTI":
            # Cerca in tutti i clienti diretti
            if self.diretti_path.exists():
                for client_dir in self.diretti_path.iterdir():
                    if client_dir.is_dir() and not client_dir.name.startswith("_"):
                        readme = client_dir / "README.md"
                        if readme.exists():
                            todos.extend(self._extract_todos_from_file(readme))
        
        return todos
    
    def _extract_todos_from_file(self, filepath: Path) -> List[Dict]:
        """
        Estrae TODO da un file markdown.
        
        Cerca pattern come:
        - [ ] task description
        - - task description [status]
        - task description (in sezioni TODOLIST o TODO)
        
        Returns:
            Lista di dict con: {file, line, text, context}
        """
        todos = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            in_todo_section = False
            current_section = None
            
            for i, line in enumerate(lines, start=1):
                # Identifica sezioni TODO
                if re.search(r'###?\s+(TODO|TODOLIST|Mia todolist)', line, re.IGNORECASE):
                    in_todo_section = True
                    current_section = line.strip()
                    continue
                elif line.startswith('#'):
                    # Nuova sezione, uscire da TODO section se non è TODO
                    if not re.search(r'TODO', line, re.IGNORECASE):
                        in_todo_section = False
                        current_section = line.strip()
                
                # Cerca pattern TODO
                # Pattern 1: - [ ] task o - [x] task
                match_checkbox = re.match(r'^-\s*\[([ x])\]\s+(.+)$', line.strip())
                if match_checkbox:
                    todos.append({
                        'file': str(filepath.relative_to(self.workspace_root)),
                        'line': i,
                        'text': match_checkbox.group(2).strip(),
                        'context': current_section or 'unknown',
                        'completed': match_checkbox.group(1).lower() == 'x'
                    })
                    continue
                
                # Pattern 2: - task description [status] (in sezione TODO)
                if in_todo_section:
                    match_dash = re.match(r'^-\s+(.+)$', line.strip())
                    if match_dash:
                        text = match_dash.group(1).strip()
                        # Estrai status se presente (es. [da fare], [in corso], ecc.)
                        completed = bool(re.search(r'\[(conclus|fatto|completat)', text, re.IGNORECASE))
                        todos.append({
                            'file': str(filepath.relative_to(self.workspace_root)),
                            'line': i,
                            'text': text,
                            'context': current_section or 'unknown',
                            'completed': completed
                        })
                        
        except Exception as e:
            print(f"Warning: Errore leggendo {filepath}: {e}")
            
        return todos
    
    def match_email_to_todos(
        self,
        email_data: Dict,
        todos: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """
        Match email con TODO basato su vari criteri.
        
        Args:
            email_data: Dict con chiavi:
                - subject: oggetto email (pulito)
                - attilio_instructions: istruzioni esplicite se da Attilio
                - preview: preview contenuto
                - from_name: nome mittente
                - society: società se presente
            todos: Lista TODO da file
            
        Returns:
            Lista di tuple (todo, confidence_score) ordinata per score decrescente
        """
        matches = []
        
        # Estrai keyword dall'email
        subject_keywords = self._extract_keywords(email_data.get('subject', ''))
        preview_keywords = self._extract_keywords(email_data.get('preview', ''))
        all_keywords = set(subject_keywords + preview_keywords)
        
        # Dati aggiuntivi
        attilio_instr = email_data.get('attilio_instructions', {})
        society = email_data.get('society', '')
        from_name = email_data.get('from_name', '')
        
        for todo in todos:
            # Salta TODO già completati
            if todo.get('completed', False):
                continue
                
            score = 0.0
            
            # Match su istruzioni esplicite di Attilio
            if attilio_instr:
                target_person = attilio_instr.get('target_person', '')
                if target_person and target_person.lower() in todo['text'].lower():
                    score += 0.3
                    
            # Match su ticket reference (es. OP# 02698455)
            ticket_match = re.search(r'OP#\s*(\d+)', email_data.get('subject', ''))
            if ticket_match:
                ticket_num = ticket_match.group(1)
                if ticket_num in todo['text']:
                    score += 0.5  # Match forte su ticket
            
            # Match su keyword progetti
            todo_keywords = self._extract_keywords(todo['text'])
            common_keywords = all_keywords.intersection(set(todo_keywords))
            
            if common_keywords:
                # Peso basato su numero keyword in comune e rarità
                keyword_score = len(common_keywords) * 0.15
                score += min(keyword_score, 0.4)  # Cap a 0.4
            
            # Match su società menzionata
            if society and society.upper() in todo['text'].upper():
                score += 0.2
            
            # Match su nome persona (es. Alessandro, Fabio)
            if from_name and from_name in todo['text']:
                score += 0.15
            
            # Match su parole chiave tecniche specifiche
            tech_keywords = {
                'InPost', 'Shopify', 'AS400', 'GCAT', 'Lotrek',
                'Tyre24', 'Weroad', 'fatturazione elettronica',
                'dashboard', 'carichi', 'feed', 'API'
            }
            
            for tech in tech_keywords:
                if tech.lower() in email_data.get('subject', '').lower():
                    if tech.lower() in todo['text'].lower():
                        score += 0.25
                        break
            
            # Se c'è qualche match, aggiungi alla lista
            if score > 0:
                matches.append((todo, score))
        
        # Ordina per score decrescente
        matches.sort(key=lambda x: x[1], reverse=True)

        # Cap confidence_action a 0.50 se nessun TODO trovato nei file reali.
        # La storia del thread embedded nel corpo email NON costituisce prova
        # di un TODO esistente — solo una corrispondenza fisica nei file vale.
        if not matches:
            # Segnala al caller che non è stato trovato nulla: il caller deve
            # cappare confidence_action a 0.50 indipendentemente da altre fonti.
            pass  # matches è già vuota — il caller riceve lista vuota = nessun match
        
        return matches
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Estrae keyword rilevanti da testo.
        
        Rimuove stopword e mantiene parole tecniche/significative.
        """
        # Converti in lowercase e rimuovi punteggiatura
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Stopword italiane comuni
        stopwords = {
            'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una',
            'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
            'e', 'o', 'ma', 'se', 'che', 'del', 'della', 'dei',
            'è', 'sono', 'ho', 'hai', 'ha', 'hanno',
            'mi', 'ti', 'si', 'ci', 'vi',
            're', 'fwd', 'r'  # Prefissi email
        }
        
        # Split e filtra
        words = text.split()
        keywords = [
            w for w in words
            if w not in stopwords and len(w) > 2
        ]
        
        return keywords


def main():
    """Esempio di utilizzo standalone per testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python match_todos.py <workspace_root> [email_json]")
        sys.exit(1)
    
    workspace_root = sys.argv[1]
    
    # Email di esempio se non fornita
    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            email_data = json.load(f)
    else:
        # Esempio hardcoded per test
        email_data = {
            'subject': 'InPost e numero di telefono',
            'from_name': 'Alessandro',
            'society': 'SPORTIT SRL',
            'preview': 'Sto verificando il mapping del numero di telefono nel feed per Meta...',
            'attilio_instructions': {}
        }
    
    # Inizializza matcher
    matcher = TodoMatcher(workspace_root)
    
    # Trova TODO nell'area COLZANI
    print("🔍 Cerco TODO in area COLZANI...")
    todos = matcher.find_todos_in_area("COLZANI", "SPORTIT SRL")
    print(f"   Trovati {len(todos)} TODO")
    
    # Match con email
    print("\n🎯 Match email con TODO esistenti...")
    matches = matcher.match_email_to_todos(email_data, todos)
    
    if matches:
        print(f"\n✅ Trovati {len(matches)} match:")
        for todo, score in matches[:5]:  # Top 5
            print(f"\n   Score: {score:.2f}")
            print(f"   File: {todo['file']}:{todo['line']}")
            print(f"   TODO: {todo['text'][:100]}")
    else:
        print("\n❌ Nessun match trovato - probabilmente è un nuovo task")


if __name__ == '__main__':
    main()
