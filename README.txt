1) arrivé du client à la biobank
Enregistrement d'un nouveau client
Enregistrement d'un projet pour le client enregistré
Enregistrement d'un depot pour le projet crée

information dépot

nom et prénoms du déposant
date et heure du dépot
date et heure du transport
température du transport
documents déposé

- fiche de renseignement
- cahier d’observation



1) Formulaire de dépôt
when client selected
look for its project

2) check if we validate before create sample

ajouter une page de demmarage pour Echantillon (Humain, Animale, Végétale ect...)

Fiche de dépôt

Patient
- fiche de renseignement des échantillons oui non
- ajouter consentement radio button oui non , input date, fichier
- cahier d'observation

- code biobank générer chez le patient un patient un code biobank

client
catégorie
Unité institu pasteur
Enlever sample


Echantillon
- couleur de tube
- volume / concentration + unité
- nombre de tube
- code échantillon
- type d'echantillon

Code impression
- Code patient
- code biobank
- code aliquot

EXP :
HypoTC18CHUC003
HU0000000001
3SURur2-fn-rouge

##TODO
1) search liste of sample +
2) select what we want
3) print liste
Print




1) Reception
- fill form and attch file
- after save go to detail
- validate the reception that generate the samples
- add to basket for storage or preparation etc....


- non conformité can be added to sample at any time

so create conformity blueprint.

2)


Ajouter un bouton de conformité
Renseigner la fiche de conformité pour un échantillon
ajouter un echantillon au panier
stocker les echantillons selectionés


Voir les informations sur un echantillons


Aliquotage
Pooling
Etiquetage.



Definir les différents status d'un echantillon


received  = 0
prepared  = 1
stored    = 2
expedited = 3
destroyed = 4


définition d'un aliquot
Table aliquot
- contient un échantillon et le volume pour les différents aliquot à creér

Aliquot(par échantillon information pour la création)
AliquotItem (liste des aliquots à créer)


roles

- Administrateur
- Micro-organisme
- Echantillon
