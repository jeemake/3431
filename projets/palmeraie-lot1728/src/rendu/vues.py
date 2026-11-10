"""Cameras des vues clay, elevations et coupes (option C v5) ; rendu par render_clay.js (Playwright + three.js)."""
import json
import pathlib
import subprocess
import sys

ICI = pathlib.Path(__file__).resolve().parent
OUT = ICI.parent.parent / "out" / "rendu"
JOUR = {"sun_az": 300, "sun_el": 38, "sky": "#e9e7e2"}          # fin d'apres-midi, soleil a l'Ouest-Nord-Ouest
ZC = 4.5
ORTHO = 31.0
VUES = {
    # perspectives a 2 points de fuite (axe de visee horizontal, decentrement)
    "clay_arrivee": {"pos": [8.0, -11.0, 1.6], "target": [10.0, 6.0, 1.6], "level": True, "fov": 60, "shift": 0.22, **JOUR},
    "clay_angle": {"pos": [-7.0, -7.5, 1.6], "target": [9.0, 8.0, 1.6], "level": True, "fov": 62, "shift": 0.2, **JOUR},
    "clay_rue_ouest": {"pos": [-7.5, 10.0, 1.6], "target": [12.0, 10.0, 1.6], "level": True, "fov": 64, "shift": 0.16, **JOUR},
    "clay_patio": {"pos": [10.2, 11.4, 1.75], "target": [12.4, 18.0, 1.75], "level": True, "fov": 70, "shift": 0.22, **JOUR},
    "clay_toit": {"pos": [16.8, 8.8, 8.3], "target": [3.0, 12.5, 8.3], "level": True, "fov": 66, "shift": -0.02, **JOUR},
    "clay_locatif": {"pos": [-7.0, 34.0, 1.6], "target": [12.0, 25.0, 1.6], "level": True, "fov": 60, "shift": 0.16, **JOUR},
    "clay_aerien": {"pos": [-16.0, -20.0, 26.0], "target": [10.0, 14.0, 2.0], "fov": 42, **JOUR},
}
TRAIT = {"lines": True, "nofog": True, "sun_az": 0, "sun_el": 60}
ELEV = {
    "elev_N": {"ortho": ORTHO, "pos": [10.0, -60.0, ZC], "target": [10.0, 0.0, ZC], "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "contexte", "locatif", "arbres_m"]},
    "elev_O": {"ortho": ORTHO, "pos": [-60.0, 10.0, ZC], "target": [0.0, 10.0, ZC], "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "locatif", "arbres_m", "contexte"]},
    "elev_S": {"ortho": ORTHO, "pos": [10.0, 80.0, ZC], "target": [10.0, 0.0, ZC], "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "locatif", "arbres_m", "vegetal", "contexte"]},
    "elev_E": {"ortho": ORTHO, "pos": [80.0, 10.0, ZC], "target": [0.0, 10.0, ZC], "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "locatif", "arbres_m", "contexte"]},
    "coupe_AA": {"ortho": ORTHO, "pos": [-60.0, 10.0, ZC], "target": [0.0, 10.0, ZC], "clip": {"axis": "x", "at": 10.75, "keep": "gt"},
                 "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "locatif", "arbres_m", "contexte"]},
    "coupe_BB": {"ortho": ORTHO, "pos": [10.0, 80.0, ZC], "target": [10.0, 0.0, ZC], "clip": {"axis": "y", "at": 14.8, "keep": "lt"},
                 "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "locatif", "arbres_m", "vegetal", "contexte"]},
    "coupe_CC": {"ortho": ORTHO, "pos": [-60.0, 25.0, ZC], "target": [0.0, 25.0, ZC], "clip": {"axis": "x", "at": 7.5, "keep": "gt"},
                 "hide": ["cloture", "arbres", "vegetal_fonce", "fleur", "maison", "arbres", "couverture", "guerite", "contexte"]},
}


def rendre(nom, scene, cam, w=1600, h=1000):
    c = {**cam, "w": w, "h": h}
    out = OUT / f"{nom}.png"
    url_cam = json.dumps(c)
    subprocess.run(["node", str(ICI / "render_clay.js"), str(ICI / "clay.html"), str(OUT / scene), str(out), url_cam],
                   check=True, cwd=str(ICI))
    return out


if __name__ == "__main__":
    quoi = sys.argv[1:] or ["persp", "trait"]
    if "persp" in quoi:
        for v in ("V1", "V2"):
            for nom, cam in VUES.items():
                rendre(f"{nom}_{v}", f"scene_C_{v}.json", cam)
    if "trait" in quoi:
        for v in ("V1", "V2"):
            for nom, cam in ELEV.items():
                if v == "V2" and nom in ("coupe_CC",):
                    continue
                rendre(f"{nom}_{v}", f"scene_C_{v}.json", {**TRAIT, **cam}, w=2400, h=1500)
