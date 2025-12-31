class CapeParser:
    def __init__(self, cipher_data):
        self.registry = cipher_data['registry']
        
    def _is_numeric(self, token):
        return token.replace('.', '', 1).isdigit()

    def _resolve_ambiguity(self, token_key, prev_token):
        """
        Lógica: Deterministic Disambiguation
        Regla: If prev == "KÙ" then UD = "BABBAR"
        """
        candidates = self.registry[token_key]
        
        # Si no es una lista, no es ambiguo
        if not isinstance(candidates, list):
            return candidates

        # Lógica de resolución de polivalencia
        for candidate in candidates:
            rule = candidate.get('rule')
            if not rule: continue
            
            condition_met = False
            
            # Regla de Precedencia (Contexto Izquierdo)
            if 'prev' in rule:
                expected = rule['prev']
                if expected == "NUMERIC" and self._is_numeric(prev_token):
                    return candidate
                if expected == prev_token:
                    return candidate
        
        # Fallback por defecto (el primero de la lista)
        return candidates[0]

    def parse_sequence(self, tokens):
        """Algoritmo de Ventana Deslizante"""
        parsed_sequence = []
        
        for i, token in enumerate(tokens):
            # Manejo de Anomalías (Phase 4)
            if token == "[BROKEN]":
                parsed_sequence.append({"status": "CORRUPT", "prime": -1, "english": "[...]"})
                continue
            
            # Manejo de Hapax (Desconocidos)
            if token not in self.registry and not self._is_numeric(token):
                parsed_sequence.append({"status": "QUARANTINE", "token": f"UNK_{i}", "english": "???"})
                continue

            # Token conocido o numérico
            if self._is_numeric(token):
                parsed_sequence.append({"type": "NUM", "val": token, "english": token})
                continue

            # Resolución Contextual
            prev_val = tokens[i-1] if i > 0 else None
            resolved_obj = self._resolve_ambiguity(token, prev_val)
            
            parsed_sequence.append(resolved_obj)
            
        return parsed_sequence