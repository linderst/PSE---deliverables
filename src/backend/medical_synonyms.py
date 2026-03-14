"""
Medical German colloquial → ICD terminology mapping.

When a user types a common everyday term, we expand it with the proper
medical terminology before running the vector search. This improves recall
for colloquial language with zero additional latency.

Future extension: this dict could be loaded from a DB table or a JSON file
so non-developers can update it without code changes.
"""

# Maps lowercased colloquial terms to a list of medical equivalents
# that will be appended to the query for richer vector search.
COLLOQUIAL_EXPANSION: dict[str, list[str]] = {
    # Kreislauf / Herz
    "bluthochdruck": ["Hypertonie", "arterielle Hypertonie", "Hochdruck"],
    "niedriger blutdruck": ["Hypotonie", "Hypotonus"],
    "herzrasen": ["Tachykardie", "Palpitationen", "supraventrikuläre Tachykardie"],
    "herzstolpern": ["Herzrhythmusstörung", "Arrhythmie", "Extrasystolen"],
    "herzinfarkt": ["Myokardinfarkt", "akutes Koronarsyndrom"],
    "schlaganfall": ["Apoplex", "Apoplexie", "zerebrovaskulärer Insult", "Hirninfarkt"],
    "herzinsuffizienz": ["Herzschwäche", "Herzinsuffizienz"],
    "krampfadern": ["Varizen", "Varikosis", "Varikose"],
    "thrombose": ["Thrombose", "tiefe Beinvenenthrombose", "TVT"],
    "lungenembolie": ["Lungenembolie", "Pulmonalembolie"],

    # Stoffwechsel / Endokrin
    "diabetes": ["Diabetes mellitus", "Zuckerkrankheit", "Typ-2-Diabetes"],
    "zuckerkrankheit": ["Diabetes mellitus", "Hyperglykämie"],
    "schilddrüse": ["Schilddrüsenerkrankung", "Thyreoiditis", "Hypothyreose", "Hyperthyreose"],
    "schilddrüsenunterfunktion": ["Hypothyreose", "Myxödem"],
    "schilddrüsenüberfunktion": ["Hyperthyreose", "Thyreotoxikose"],
    "fettleibigkeit": ["Adipositas", "Obesitas", "Übergewicht"],
    "übergewicht": ["Adipositas", "Übergewicht", "BMI"],

    # Neurologie / Psyche
    "kopfschmerzen": ["Kopfschmerz", "Cephalalgie", "Migräne"],
    "migräne": ["Migräne", "Hemikranie"],
    "schwindel": ["Vertigo", "Schwindel", "Benommenheit"],
    "ohnmacht": ["Synkope", "Kollaps", "Bewusstlosigkeit"],
    "epilepsie": ["Epilepsie", "Krampfanfall", "Anfallsleiden"],
    "parkinson": ["Parkinson-Krankheit", "Morbus Parkinson"],
    "depression": ["Depression", "depressive Episode", "affektive Störung"],
    "angststörung": ["Angststörung", "Panikattacke", "Phobie"],
    "burn-out": ["Burnout", "Erschöpfungssyndrom", "Neurasthenie"],
    "demenz": ["Demenz", "Alzheimer", "kognitive Störung"],
    "alzheimer": ["Alzheimer-Krankheit", "Morbus Alzheimer", "Demenz"],
    "schlaflosigkeit": ["Insomnie", "Schlafstörung", "Einschlafstörung"],
    "schlafstörungen": ["Insomnie", "Schlafstörung", "Parasomnien"],

    # Atemwege
    "husten": ["Husten", "Pertussis", "Bronchitis"],
    "asthma": ["Asthma bronchiale", "Atemwegsobstruktion"],
    "lungenenzündung": ["Pneumonie", "Lungenentzündung"],
    "erkältung": ["Rhinitis", "Nasopharyngitis", "Infekt der oberen Atemwege"],
    "grippe": ["Influenza", "Grippe", "virale Infektion"],
    "bronchitis": ["Bronchitis", "akute Bronchitis"],
    "copd": ["COPD", "chronisch obstruktive Lungenerkrankung"],
    "kurzatmigkeit": ["Dyspnoe", "Atemnot", "Luftnot"],

    # Verdauung / Magen-Darm
    "magengeschwür": ["Ulcus ventriculi", "Magenulkus", "Ulkus"],
    "sodbrennen": ["Reflux", "Gastroösophagealer Reflux", "GERD", "Pyrosis"],
    "verstopfung": ["Obstipation", "Konstipation"],
    "durchfall": ["Diarrhö", "Diarrhoe", "Durchfall"],
    "übelkeit": ["Nausea", "Übelkeit", "Emesis"],
    "erbrechen": ["Erbrechen", "Emesis", "Vomitus"],
    "bauchschmerzen": ["Abdominalschmerz", "Bauchschmerz", "Abdominalgie"],
    "reizdarm": ["Reizdarmsyndrom", "IBS", "irritables Kolon"],
    "gallensteine": ["Cholelithiasis", "Gallenkolik", "Cholezystolithiasis"],

    # Muskel-Skelett / Schmerz
    "rückenschmerzen": ["Rückenschmerz", "Dorsalgie", "Lumbago", "Lumbalgie"],
    "kreuzschmerzen": ["Lumbago", "Kreuzschmerz", "LWS-Syndrom"],
    "arthritis": ["Arthritis", "Gelenksentzündung", "rheumatoide Arthritis"],
    "arthrose": ["Arthrose", "Gonarthrose", "Coxarthrose", "Osteoarthrose"],
    "rheuma": ["Rheumatismus", "rheumatoide Arthritis", "Kollagenose"],
    "fibromyalgie": ["Fibromyalgie", "Fibromyalgiesyndrom"],
    "bandscheibenvorfall": ["Bandscheibenprolaps", "Diskusprolaps", "Hernie"],
    "osteoporose": ["Osteoporose", "Knochenschwund"],
    "gicht": ["Gicht", "Arthritis urica", "Hyperurikämie"],

    # Haut
    "neurodermitis": ["atopische Dermatitis", "Neurodermitis", "atopisches Ekzem"],
    "schuppenflechte": ["Psoriasis", "Psoriasis vulgaris"],
    "akne": ["Akne", "Acne vulgaris"],
    "ekzem": ["Ekzem", "Dermatitis"],
    "urtikaria": ["Urtikaria", "Nesselsucht", "Quaddeln"],
    "nesselsucht": ["Urtikaria", "Nesselsucht"],

    # Urologie / Niere
    "harnwegsinfekt": ["Harnwegsinfektion", "Zystitis", "Blasenentzündung"],
    "blasenentzündung": ["Zystitis", "Harnwegsinfektion", "Urethritis"],
    "niereninsuffizienz": ["Niereninsuffizienz", "renale Insuffizienz", "chronische Nierenerkrankung"],
    "nierensteine": ["Nephrolithiasis", "Urolithiasis", "Harnsteine"],

    # Gynäkologie / Geburtshilfe
    "endometriose": ["Endometriose"],
    "gebärmuttererkrankung": ["Uteruserkrankung", "Myom", "Endometriose"],
    "wechseljahre": ["Menopause", "Klimakterium", "Menopausensyndrom"],
    "pcks": ["polyzystisches Ovarsyndrom", "PCOS"],

    # Onkologie (allgemein)
    "krebs": ["Karzinom", "Neoplasie", "Tumor", "maligne Neubildung"],
    "tumor": ["Neoplasie", "Tumor", "Karzinom"],
    "lymphom": ["Lymphom", "Hodgkin", "Non-Hodgkin-Lymphom"],
    "leukämie": ["Leukämie", "Leukose"],

    # Infektionskrankheiten
    "corona": ["COVID-19", "SARS-CoV-2", "Coronavirus"],
    "covid": ["COVID-19", "SARS-CoV-2"],
    "hepatitis": ["Hepatitis", "Leberentzündung"],
    "hiv": ["HIV", "AIDS", "Immunschwächesyndrom"],
    "tuberkulose": ["Tuberkulose", "TBC", "Mycobacterium tuberculosis"],

    # Augen
    "grauer star": ["Katarakt", "Linsentrübung"],
    "grüner star": ["Glaukom", "Augeninnendruck"],
    "makuladegeneration": ["Makuladegeneration", "AMD"],

    # Zahnarzt / HNO
    "hörverlust": ["Schwerhörigkeit", "Hypakusis", "Hörsturz"],
    "tinnitus": ["Tinnitus", "Ohrgeräusch"],
    "schnarchen": ["Schnarchen", "Schlafapnoe", "obstruktive Schlafapnoe"],
}


def expand_query(q: str) -> str:
    """
    Expand a user query with medical terminology.
    Returns an enriched query string.
    """
    q_lower = q.lower().strip()
    
    # Check for exact term match first
    for colloquial, medical_terms in COLLOQUIAL_EXPANSION.items():
        if colloquial in q_lower:
            expanded = q + " " + " ".join(medical_terms)
            return expanded
    
    return q
