# Nebula Drift

Un petit projet d'animation Python présentant un vaisseau spatial naviguant dans une nébuleuse procédurale, avec étoiles parallaxe et effets de particules.

## Description

Ce programme crée une animation interactive d'un petit vaisseau spatial dans un environnement spatial. Le vaisseau peut être contrôlé avec les touches du clavier pour naviguer à travers les étoiles.

## Installation

1. Assurez-vous d'avoir Python installé (version 3.7 ou supérieure)
2. Installez les dépendances requises :
   ```
   pip install -r requirements.txt
   ```

## Utilisation

Lancez le programme avec :
```
python main.py
```

### Contrôles

- **Flèche Gauche / A**: Tourner le vaisseau à gauche
- **Flèche Droite / D**: Tourner le vaisseau à droite  
- **Flèche Haut / W**: Propulser le vaisseau vers l'avant
- **Échap**: Quitter l'application

## Fonctionnalités

- Vaisseau spatial contrôlable avec visualisation de propulsion
- Arrière-plan spatial avec étoiles aléatoires
- Effet de particules pour la propulsion du vaisseau
- Gestion des bordures d'écran (le vaisseau réapparaît de l'autre côté)

## Technologies utilisées

- Python
- Pygame pour l'animation et l'interaction
- Math pour les calculs de rotation
- Random pour la génération procédurale

## Auteur

Projet créé pour l'animation d'un petit vaisseau spatial dans l'espace.