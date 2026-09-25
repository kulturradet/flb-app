"""Fond for lyd og bilde — tildelinger per år. Aggregert framstilling.

Tre variabler: år, beløp, antall.

Leser bare app/data/flb_per_aar.csv, som ligger ved siden av denne filen i
repoet. Ingen tilgang til $HABITUS_DATA, ingen radnivådata, ingen mottakere.
Det er det som gjør denne appen trygg å kjøre utenfor egen maskin.

Datafilen bygges av mart/flb_per_aar.py.

Om datagrunnlaget: årene til og med 2024 er summert fra enkelttildelinger.
2025 er et totaltall for hele året fra økonomisystemet — detaljserien dekker
bare til og med juni 2025 (289 rader, 26 747 000 kr), og ville vist et halvt
år som om det var et helt. Byggetidspunkt, kildehash og merknader ligger i
app/data/flb_per_aar.meta.json. Dette hører hjemme i dokumentasjonen, ikke i
framstillingen.

Kjør lokalt:
    .venv\\Scripts\\python.exe -m streamlit run app\\flb_aggregat.py
"""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parent / "data" / "flb_per_aar.csv"

st.set_page_config(page_title="FLB — tildelinger per år", layout="wide")


def kr(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")


@st.cache_data
def last(sti: str) -> pd.DataFrame:
    return pd.read_csv(sti)


if not DATA.exists():
    st.error(f"Finner ikke {DATA.name}. Kjør mart/flb_per_aar.py først.")
    st.stop()

d = last(str(DATA))

st.title("Fond for lyd og bilde — tildelinger per år")
st.caption(
    "Norsk kassettavgiftsfond til og med 1999, Fond for lyd og bilde fra 2000. "
    "Nominelle kroner."
)

siste = d.iloc[-1]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Periode", f"{d['aar'].min()}–{d['aar'].max()}")
k2.metric(f"Tildelt {siste['aar']}", kr(siste["belop"]))
k3.metric(f"Tildelinger {siste['aar']}", kr(siste["antall"]))
k4.metric("Tildelt i hele serien", kr(d["belop"].sum()))

maal = st.radio("", ["Beløp", "Antall"], horizontal=True, label_visibility="collapsed")
felt, tittel = ("belop", "Tildelt beløp") if maal == "Beløp" else ("antall", "Antall tildelinger")

st.altair_chart(
    alt.Chart(d)
    .mark_bar(color="#1f2937")
    .encode(
        x=alt.X("aar:O", title="År"),
        y=alt.Y(f"{felt}:Q", title=tittel),
        tooltip=[
            alt.Tooltip("aar:O", title="År"),
            alt.Tooltip(f"{felt}:Q", title=tittel, format=",.0f"),
        ],
    )
    .properties(height=460),
    use_container_width=True,
)

vis = d.copy()
vis["belop"] = vis["belop"].map(kr)
vis["antall"] = vis["antall"].map(kr)
vis.columns = ["År", "Beløp", "Antall"]

with st.expander("Tall"):
    st.dataframe(vis, use_container_width=True, hide_index=True)

st.download_button(
    "Last ned (CSV)",
    d.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"flb_per_aar_{d['aar'].min()}_{d['aar'].max()}.csv",
    mime="text/csv",
)

with st.expander("Om statistikken"):
    st.markdown(
        """
Populasjonen er alle tilskudd gitt fra Fond for lyd og bilde.

Enhet i statistikken er prosjekttilskudd. Samme virksomhet kan motta flere
prosjekttilskudd innenfor samme søknadsperiode.

Beløp for tilskuddet er vedtatt beløp for hvert prosjekttilskudd.

Finansieringen kan komme fra flere kilder, vanligvis midler tildelt Fond for
lyd og bilde. Under koronapandemien var også tilleggsbevilgninger tilgjengelig
for Fond for lyd og bilde. Noen vedtak under pandemien var finansiert fra annen
kilde enn Fond for lyd og bildes eget budsjett. Det er grunnen til at volum på
vedtak langt overgår budsjett for Fond for lyd og bilde under koronapandemien.

År for tilskudd er regnskapsår vedtaket er knyttet til. Regnskapsår er valgt da
det virker å gi den mest forutsigbare fremstillingen av tildelte tilskudd over
tid. Spesielt ved bytter av saksbehandlingssystem kan alternative tidsangivelser
knyttet til vedtakstidspunkt gi et svært annerledes bilde, da det kan bli
forsinkelser i vedtaksaktivitet.

Statistikken bygger på tilskudd registrert i saksbehandlingssystem, og for de
eldste årene på arkivmateriale.
"""
    )

st.caption("Ved bruk av statistikken skal Kulturdirektoratet oppgis som kilde.")