class SyntacticReconstructor:
    """
    SDA-03: Topology Shift
    Transforma: [SUJETO] [OBJETO] [VERBO] -> [SUJETO] [VERBO] [OBJETO]
    """
    def reconstruct(self, parsed_vector):
        subj = []
        verb = []
        dobj = [] # Direct Object
        iobj = [] # Indirect Object
        others = []

        i = 0
        while i < len(parsed_vector):
            token = parsed_vector[i]
            
            # Si es corrupto o desconocido, lo pasamos directo a 'others'
            if "status" in token:
                others.append(token.get("english", "???"))
                i += 1
                continue

            t_type = token.get("type", "MISC")
            english_val = token.get("english", "")

            # Lógica de Enrutamiento Sintáctico
            if t_type == "ROLE" or t_type == "PERSON":
                subj.append(english_val)
            
            elif t_type == "VERB_ROOT":
                # Aquí iría la lógica MCVG (Conjugación), simplificada:
                verb.append(english_val)
                
            elif t_type == "PREP":
                # Detectar objeto indirecto (Ej: ana Enlil = to Enlil)
                iobj.append(english_val) # "to"
                if i + 1 < len(parsed_vector):
                    next_t = parsed_vector[i+1]
                    iobj.append(next_t.get("english", ""))
                    i += 1 # Saltamos el siguiente porque ya lo consumimos
            
            elif t_type in ["OBJ", "LOC", "NUM", "ADJ", "SUFFIX"]:
                dobj.append(english_val)
            
            else:
                others.append(english_val)
            
            i += 1

        # Ensamblaje Final (SHUFFLE)
        # Orden Inglés: Sujeto + Verbo + Objeto Directo + Objeto Indirecto + Otros
        final_sentence = subj + verb + dobj + iobj + others
        
        # Limpieza de espacios y nulos
        return " ".join([w for w in final_sentence if w]).capitalize()