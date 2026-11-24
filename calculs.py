import numpy as np
import pandas as pd
import yfinance as yf

JOURS_BOURSE_PAR_AN = 252  # nombre moyen de jours de cotation dans une année


def telecharger_prix(tickers, periode):
    """Télécharge les prix de clôture (ajustés des dividendes et divisions d'actions)."""
    donnees = yf.download(tickers, period=periode, auto_adjust=True, progress=False)
    prix = donnees["Close"]
    # Les bourses européennes et américaines n'ont pas les mêmes jours fériés :
    # on recopie le dernier prix connu pour combler les trous.
    return prix.ffill().dropna()


def moyenne_mobile(serie, fenetre):
    """Moyenne des `fenetre` derniers prix, recalculée chaque jour."""
    return serie.rolling(fenetre).mean()


def base_100(prix):
    """Ramène chaque courbe à 100 au premier jour pour comparer des prix différents."""
    return prix / prix.iloc[0] * 100


def rendement(serie):
    """Gain ou perte en % entre le premier et le dernier jour de la période."""
    return serie.iloc[-1] / serie.iloc[0] - 1


def volatilite_annualisee(serie):
    """Écart-type des variations quotidiennes, ramené à une année."""
    variations = serie.pct_change().dropna()
    return variations.std() * np.sqrt(JOURS_BOURSE_PAR_AN)


def tableau_comparaison(prix, noms):
    """Construit le tableau rendement / volatilité pour chaque colonne de `prix`."""
    lignes = []
    for ticker in prix.columns:
        lignes.append({
            "Nom": noms.get(ticker, ticker),
            "Ticker": ticker,
            "Rendement": rendement(prix[ticker]),
            "Volatilité annualisée": volatilite_annualisee(prix[ticker]),
        })
    return pd.DataFrame(lignes)
