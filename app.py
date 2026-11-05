# ============================================================
# Lancer avec : streamlit run app_etudiant.py
# ============================================================

import re
from fractions import Fraction
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Application Bigramme")


# ------------------------------------------------------------
# 1) Pretraitement
# ------------------------------------------------------------
def decouper_phrases(texte):
    """Decoupe le corpus en phrases (., !, ? et retour a la ligne)."""
    phrases = re.split(r"[.!?\n]+", texte)
    resultat = []
    for p in phrases:
        if p.strip() != "":
            resultat.append(p.strip())
    return resultat


def decouper_mots(phrase):
    """Met en minuscules et recupere les mots (sans ponctuation)."""
    return re.findall(r"\w+", phrase.lower())


# ------------------------------------------------------------
# 2) Entraînement : compter les bigrammes
# ------------------------------------------------------------
def entrainer_modele(corpus):
    bigrammes = {}      # {(mot1, mot2): nombre}
    contextes = {}      # {mot1: nombre}
    vocabulaire = set() # mots distincts (sans <s> et </s>)

    for phrase in decouper_phrases(corpus):
        mots = decouper_mots(phrase)
        if len(mots) == 0:
            continue

        mots_marques = ["<s>"] + mots + ["</s>"]

        for m in mots:
            vocabulaire.add(m)

        for i in range(len(mots_marques) - 1):
            m1 = mots_marques[i]
            m2 = mots_marques[i + 1]
            bigrammes[(m1, m2)] = bigrammes.get((m1, m2), 0) + 1
            contextes[m1] = contextes.get(m1, 0) + 1

    return bigrammes, contextes, vocabulaire


# ------------------------------------------------------------
# 3) Fonctions d'affichage des fractions
# ------------------------------------------------------------
def texte_fraction(f):
    """Affiche une Fraction : 2/11, ou 1 si le denominateur vaut 1."""
    if f.denominator == 1:
        return str(f.numerator)
    return str(f.numerator) + "/" + str(f.denominator)


def latex_fraction(f):
    """Fraction simplifiee en LaTeX."""
    if f.denominator == 1:
        return str(f.numerator)
    return "\\frac{" + str(f.numerator) + "}{" + str(f.denominator) + "}"


def valeur_decimale(x):
    """Valeur decimale lisible (notation scientifique si tres petite)."""
    x = float(x)
    if x != 0 and x < 0.0001:
        return "{:.3e}".format(x)
    return "{:.6f}".format(x)


# ------------------------------------------------------------
# 4) Interface Streamlit
# ------------------------------------------------------------
st.markdown(
    """
    <div style="background-color:#1f4e79; padding:18px; border-radius:10px; text-align:center;">
        <h1 style="color:white; margin:0;"> Application Bigramme</h1>
        <p style="color:#d9e6f2; margin:4px 0 0 0;">
            evaluateur de phrases par Modele Bigramme (lissage de Laplace / Jeffreys)
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

corpus = st.text_area("Corpus", height=200)
phrase = st.text_area("Phrase a evaluer / Rechercher", height=80)

choix = st.radio(
    "Choisir le type de lissage :",
    ["Laplace (α = 1)", "Jeffreys (α = 0.5)"],
    horizontal=True,
)
if choix.startswith("Laplace"):
    nom_lissage = "Laplace"
    alpha_txt = "1"
    alpha = Fraction(1)
else:
    nom_lissage = "Jeffreys"
    alpha_txt = "0.5"
    alpha = Fraction(1, 2)

if st.button("Analyser la phrase"):

    # --- cas limites ---
    if corpus.strip() == "":
        st.error("Le corpus est vide !")
    elif phrase.strip() == "":
        st.error("La phrase est vide !")
    else:
        bigrammes, contextes, vocabulaire = entrainer_modele(corpus)
        V = len(vocabulaire)
        mots = decouper_mots(phrase)

        if V == 0:
            st.error("Le corpus ne contient aucun mot.")
        elif len(mots) == 0:
            st.error("La phrase ne contient aucun mot.")
        else:
            mots_marques = ["<s>"] + mots + ["</s>"]

            # ---------- Formules ----------
            st.subheader("Formules")
            st.write("Avant lissage (maximum de vraisemblance) :")
            st.latex(r"P(w_i \mid w_{i-1}) = \frac{C(w_{i-1}\, w_i)}{C(w_{i-1})}")
            st.write("Apres lissage de " + nom_lissage + " (α = " + alpha_txt + ", V = " + str(V) + ") :")
            st.latex(r"P(w_i \mid w_{i-1}) = \frac{C(w_{i-1}\, w_i) + \alpha}{C(w_{i-1}) + \alpha V}")

            # ---------- Calcul de chaque transition ----------
            lignes = []
            avant_latex = []        # fractions avant lissage
            apres_latex = []        # fractions apres lissage (non simplifiees)
            produit_apres = Fraction(1)
            produit_avant = Fraction(1)
            avant_indefini = False  # True si on tombe sur 0/0

            for i in range(len(mots_marques) - 1):
                m1 = mots_marques[i]
                m2 = mots_marques[i + 1]

                c_bi = bigrammes.get((m1, m2), 0)
                c_ctx = contextes.get(m1, 0)

                # Avant lissage : C(m1 m2) / C(m1)
                if c_ctx == 0:
                    avant_txt = str(c_bi) + "/0  (indefini)"
                    avant_indefini = True
                    avant_latex.append("\\frac{" + str(c_bi) + "}{0}")
                else:
                    f_avant = Fraction(c_bi, c_ctx)
                    produit_avant = produit_avant * f_avant
                    avant_txt = str(c_bi) + "/" + str(c_ctx)
                    avant_latex.append("\\frac{" + str(c_bi) + "}{" + str(c_ctx) + "}")

                # Apres lissage : (C(m1 m2) + alpha) / (C(m1) + alpha * V)
                num = Fraction(c_bi) + alpha
                den = Fraction(c_ctx) + alpha * V
                f_apres = num / den
                produit_apres = produit_apres * f_apres

                apres_txt = "(" + str(c_bi) + "+" + alpha_txt + ")/(" + str(c_ctx) + "+" + alpha_txt + "×" + str(V) + ")"
                apres_latex.append("\\frac{" + str(c_bi) + "+" + alpha_txt + "}{" + str(c_ctx) + "+" + alpha_txt + "\\times " + str(V) + "}")

                lignes.append({
                    "Bigramme": m1 + " -> " + m2,
                    "Avant lissage": avant_txt,
                    "Apres lissage": apres_txt,
                    "Simplifie": texte_fraction(f_apres),
                    "Valeur": valeur_decimale(f_apres),
                })

            # ---------- Tableau des transitions ----------
            st.subheader("Detail des transitions")
            st.dataframe(pd.DataFrame(lignes), hide_index=True)

            # ---------- Probabilite de la phrase ----------
            st.subheader("Probabilite de la phrase")

            st.write("Avant lissage :")
            if avant_indefini:
                st.latex(" \\times ".join(avant_latex) + " = \\text{indefini (division par 0)}")
            else:
                st.latex(" \\times ".join(avant_latex) + " = " + latex_fraction(produit_avant))

            st.write("Apres lissage de " + nom_lissage + " :")
            st.latex(" \\times ".join(apres_latex))
            st.latex(
                "= " + latex_fraction(produit_apres)
                + " \\approx " + valeur_decimale(produit_apres)
            )