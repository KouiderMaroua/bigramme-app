# Application Bigramme

Petite application Streamlit qui **évalue une phrase** à l'aide d'un
modèle de langage **bigramme** entraîné sur un corpus saisi par l'utilisateur,
avec choix entre deux lissages :

- **Laplace** (α = 1)
- **Jeffreys** (α = 0.5)

## Fonctionnalités

- Découpage automatique du corpus en phrases et en mots
- Calcul de P(wᵢ | wᵢ₋₁) **avant** et **après** lissage
- Affichage des fractions exactes (via `Fraction`)
- Détail transition par transition dans un tableau
- Produit des probabilités de la phrase entière

## Formules utilisées

Avant lissage :

$$P(w_i \mid w_{i-1}) = \frac{C(w_{i-1} w_i)}{C(w_{i-1})}$$

Après lissage (Laplace / Jeffreys) :

$$P(w_i \mid w_{i-1}) = \frac{C(w_{i-1} w_i) + \alpha}{C(w_{i-1}) + \alpha V}$$

où `V` est la taille du vocabulaire (mots distincts, hors `<s>` et `</s>`).

## Lancer en local

```bash
git clone https://github.com/KouiderMaroua/bigramme-app.git
cd bigramme-app
pip install -r requirements.txt
streamlit run app.py
```
##  Démo en ligne
https://bigramme-app.streamlit.app/
