# Projekt Software Engineering - Medcode

## Organisatorische Rollen
Felix: Key Account Manager
Alex: Master-Tracker 
Stefan: Chief Deliverable Officer 
Christian: Quality Evangelist
Dennis &amp; Julien: Sitzungsleitung und Protokollführung

### Trello (Arbeitsplan)
https://trello.com/invite/b/699c50bc8934bc6d26e464a5/ATTI1d9d3acc8e273c0cf821f590b0f7a0626D898DDD/pse

## Beschreibung
Dieses Projekt zielt darauf ab, medizinische Antworten und einen Überblick über medizinische Diagnosen zu bieten. Nutzer können nach dem Namen der Krankheit oder nach dem ICD-10-Code (den sie auf ihrer Arztrechnung finden) suchen. Das Suchwort wird in einer Datenbank nach Übereinstimmungen durchsucht, und diese Übereinstimmung wird dann an ein LLM weitergeleitet, um die folgenden drei Fragen zu beantworten:
- Was ist das?
- Wer behandelt das?
- Wie wird es behandelt?

## Benutzung (Beispiel)
Der Nutzer findet auf der Arztrechnung den Code J18.9. Da er nicht weiß, was dieser bedeutet, sucht er auf der Website med.qm1.ch nach J18.9. Der Nutzer erfährt, dass J18 die Kategorie für „Pneumonie“ ist und kann unter „Was ist das?“ nachlesen, dass dies gemeinhin als „Lungenentzündung“ bezeichnet wird. Diese wird in der Regel vom Hausarzt behandelt, in manchen Fällen jedoch an einen Lungenfacharzt überwiesen. 
Außerdem erfährt der Nutzer, dass eine Lungenentzündung in der Regel mit Antibiotika behandelt wird. Der Nutzer hat jedoch noch offene Fragen. Der Nutzer stellt diese Folgefragen im Suchfeld unten und erfährt, dass ein Eisbad keine gute Idee ist und dass es in der Regel 3–6 Wochen dauert, bis sich der Körper erholt hat. Das hatte der Arzt ursprünglich auch erklärt, und jetzt erinnert sich der Nutzer wieder daran.
Leider hat der Nutzer vergessen, ein Arztzeugnis anzufordern, und möchte nicht noch einmal zum Arzt gehen. Dann entdeckt der Nutzer den Link zur Plattform extradoc.ch, wo er das Arztzeugnis bequem online erhalten kann.

## Setup
See setup.md for further details

## Struktur
To be added


- [Test Anleitung](test_anleitung.md)
