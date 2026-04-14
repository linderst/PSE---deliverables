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