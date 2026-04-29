# Todo for this branch

## Gemini Api 503 error
Momentan wird bei jedem vector search ein embedding per gemini api gemacht.  
Für Paralellisierung absolut unbrauchbar, da somit immer mehere API calls -> API überlastet, bzw
extrem von Gemini abhängig.

Lösung:
* lokales Embedding model


## Testevaluation
Gleichzeitiges testen zwischen den beiden Systemen
Paralell und seriell.



# changes
* in dependecies.py 
    use_parallel=False gibt an ob parallel search oder nicht -> bleibt nicht also wieder to delete

* in dockerfile (backend)
preload model into docker image

* in requirements.txt
Model : sentence-transformers

* in database.sql
icd_embedding tabel, dim von 3072 auf 384 für lokales modell

* in import_icd.py
genau gleiche
