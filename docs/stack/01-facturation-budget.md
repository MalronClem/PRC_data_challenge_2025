# 01 — Facturation et budget (Google Cloud)

## Rôle

Rattacher le projet Google Cloud `prc-data-challenge-2025` à un compte de facturation actif, condition obligatoire pour utiliser le free tier de Cloud Storage et de BigQuery, et surveiller les dépenses.

## Pourquoi ce choix

- L'essai gratuit Google Cloud (300 $ sur 90 jours) avait déjà été utilisé et était terminé : il n'est accessible qu'une fois par personne.
- Le free tier ("Always Free") exige un compte de facturation **actif**. Le compte d'essai terminé a donc été passé en compte complet (bouton « Changer » dans le bandeau de la console).
- Conséquence : il n'y a plus de filet de sécurité. Tout usage au-delà des limites gratuites est facturé sur la carte enregistrée.

## Configuration

- **Compte de facturation** : « Mon compte de facturation », passé en compte complet.
- **Projet** : `prc-data-challenge-2025`, associé à ce compte de facturation.
- **Budget** : « Alerte budget PRC »
  - Période : mensuelle
  - Portée : tout le compte de facturation (couvre aussi les futurs projets)
  - Montant : 1 €
  - Seuils : 50 %, 90 %, 100 %, déclenchés sur les dépenses **réelles**
  - Notification : e-mail aux administrateurs de la facturation
- **Plafond de dépenses** : non activé. La fonction « Budgets & caps » (en Preview) permet de mettre des services en pause en cas de dépassement. À étudier avant activation.

## Où le retrouver

Console → Menu ☰ → Facturation → Cost control → **Budgets & caps**.

## Coûts et limites

- Une alerte de budget **prévient mais ne bloque rien** : les services continuent de tourner.
- Les coûts apparaissent dans la console avec un délai pouvant aller jusqu'à 24 h.
- Free tier Google Cloud : sans date de fin, mais Google peut le modifier avec 30 jours de préavis.
- Risque principal : une erreur de manipulation (ressource dans une région hors free tier, machine virtuelle oubliée), pas l'usage normal du projet.
