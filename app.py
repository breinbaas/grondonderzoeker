import streamlit as st
from pyproj import Transformer
import pandas as pd
import numpy as np
import pydeck as pdk


# some constants derived from geoweb
XLEFT = 109100
XRIGHT = 456625
YTOP = 494125
YBOTTOM = 456626
XINTERVAL = 2375
YINTERVAL = 1875

ROWNAMES = "ABCDEFGHJKLMNOPQRSTU"  # note the skipped I


def xy_to_code(x: float, y: float) -> str:
    """Haal de vakcode op obv de gegeven x, y RD coordinaten. Let op; de controle of x en y binnen het gebied vallen moet vooraf gebeuren!"""
    dx = x - XLEFT
    dy = YTOP - y

    ix = int(dx / XINTERVAL) + 1
    iy = int(dy / YINTERVAL)

    return f"{ROWNAMES[iy]}{ix:02d}"


# RD to WGS84 transformer
transformer = Transformer.from_crs(28992, 4326)

st.set_page_config(layout="wide")

st.title("Waternet Grondonderzoeker")

st.markdown(
    """
Vul de RD coordinaten en tijdelijke naam in van het grondonderzoek dat je uit wilt voeren
"""
)

user_data = st.text_area("Grondonderzoek", "124523,457425,S\n142259,470561,S")

data = {"x": [], "y": [], "lat": [], "lon": [], "naam": [], "vak": []}

if st.button("Bepaal vaknamen"):
    msg = ""
    for line in user_data.split("\n"):
        try:
            x, y, t = line.split(",")
            x = float(x)
            y = float(y)

            if x < XLEFT or x > XRIGHT or y > YTOP or y < YBOTTOM:
                msg += f"{t} valt met x={x} en y={y} buiten het vaknamen gebied van Waternet en wordt verder genegeerd\n"
                continue

            lat, lon = transformer.transform(x, y)

        except Exception as e:
            continue

        data["x"].append(x)
        data["y"].append(y)
        data["naam"].append(t)
        data["vak"].append(xy_to_code(x, y))
        data["lat"].append(lat)
        data["lon"].append(lon)

    if msg != "":
        st.warning(msg)

    if len(data["x"]) == 0:
        st.stop()

    # create the lines with the name with the vakcode
    lines = ""
    for i in range(len(data["lat"])):
        x = data["x"][i]
        y = data["y"][i]
        name = data["naam"][i]
        vak = data["vak"][i]
        lines += f"{x},{y},{name} {vak}\n"

    final_data = st.text_area("Grondonderzoek met vakcode", lines)

    st.map(pd.DataFrame.from_dict(data))
