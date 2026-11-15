"""Blocs de la bibliotheque Capitude / Archibooks (bucket prive blocs-archibooks) inseres dans les SVG.

- `sync()` telecharge en lecture seule les DXF utiles dans un cache local (hors depot), avec la cle de
  service deja configuree dans l'environnement (SUPABASE_URL, SUPABASE_SERVICE_KEY), et controle le SHA-256
  publie dans le catalogue.
- `Bibliotheque.defs()` convertit chaque bloc (geometrie native, metres, Y vers le haut) en <symbol> SVG ;
  les instances sont des <use> transformes (echelle, rotation, miroir) : les maitres ne sont jamais modifies.
- Les textures 2 x 2 m sont repetees puis recadrees exactement au polygone par un clipPath (trous compris).

Opacites de depart (regle GRAPHISME-OPACITES) : canopees 45-65 %, massifs 55-70 %, sols 55-70 %,
pas 75-85 %, eau 10-25 %, mobilier / personnes 70-85 %, portes 100 %.
"""
import hashlib
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(os.environ.get("ARCHIBOOKS_BLOCS", ROOT / ".cache_blocs"))
BUCKET = "blocs-archibooks"

# blocs utilises par le dossier (identifiants du catalogue Capitude)
UTILISES = [
    "porte_battante_90", "porte_double",
    "arbre_frangipanier", "arbre_feuilles_ovales", "arbre_touffes_frisees", "arbre_feuillage_dense",
    "texture_pierre", "texture_paves", "texture_eau", "texture_granulat_fin", "texture_couvre_sol",
    "texture_litiere", "texture_massif_tropical", "texture_pas_irreguliers", "texture_pierre_bandes",
    "veg_coupe_palmier_retombant", "veg_coupe_arbre_grande_canopee", "veg_coupe_petit_feuillu_dense",
    "veg_coupe_bosquet_etage", "veg_coupe_grandes_feuilles", "veg_coupe_fougeres",
    "pers_pmd_005_marche_dos", "pers_pmd_042_debout_face", "pers_pmd_108_assis_profil", "pers_pmd_130_marche_face",
    "pers_tt_02_marche_profil_sac", "pers_tt_03_robe_motifs_face",
]

# style par calque : (trait px, couleur, remplissage)
STYLE = {
    "BLOC_MUR": (1.4, "#000000", "none"), "BLOC_OUVRANT": (1.0, "#000000", "none"),
    "BLOC_DEBATTEMENT": (0.5, "#000000", "none"), "BLOC_AXE": (0.4, "#000000", "none"),
    "BLOC_CONTOUR": (0.5, "#000000", "none"), "BLOC_HACHURE": (0.35, "#3a3a3a", "none"),
    "BLOC_TEXTURE": (0.3, "#6b6b6b", "none"),
    "BLOC_FEUILLAGE": (0.3, "#3a3a3a", "none"), "BLOC_BRANCHES": (0.35, "#3a3a3a", "none"),
    "BLOC_TRONC": (0.7, "#2a2a2a", "none"),
}
DEF_STYLE = (0.35, "#2b2b2b", "none")


def _get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "apikey": key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def sync(ids=UTILISES):
    """Telecharge catalogue + DXF dans le cache (lecture seule), verifie les SHA-256."""
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY absents : synchroniser le cache autrement.")
    CACHE.mkdir(parents=True, exist_ok=True)
    cat = _get(f"{url}/storage/v1/object/{BUCKET}/catalogue.json", key)
    (CACHE / "catalogue.json").write_bytes(cat)
    blocs = {b["id"]: b for b in json.loads(cat)["blocs"]}
    for i in ids:
        b = blocs[i]
        dest = CACHE / b["dxf"]
        if dest.exists():
            continue
        data = _get(f"{url}/storage/v1/object/{BUCKET}/{b['dxf']}", key)
        sha = b.get("sha256_dxf") or (b.get("sha256") or {}).get("dxf")
        if sha and hashlib.sha256(data).hexdigest() != sha:
            raise RuntimeError(f"SHA-256 different pour {b['dxf']} : synchronisation arretee")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)


def sync_base(prefixes=("vegetation-elcroquis-v1/",)):
    """Catalogue vivant (table blocs_archibooks, lecture seule) + DXF des dossiers recents, SHA-256 controle."""
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY absents")
    rows = json.loads(_get(f"{url}/rest/v1/blocs_archibooks?select=id,categorie,bloc_dxf,chemin_dxf,sha256_dxf,"
                           f"dimensions,insertion,actif&actif=eq.true", key))
    (CACHE / "catalogue_base.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        p = r.get("chemin_dxf")
        if not p or not p.startswith(prefixes) or (CACHE / p).exists():
            continue
        data = _get(f"{url}/storage/v1/object/{BUCKET}/{p}", key)
        if hashlib.sha256(data).hexdigest() != r["sha256_dxf"]:
            raise RuntimeError(f"SHA-256 different pour {p}")
        (CACHE / p).parent.mkdir(parents=True, exist_ok=True)
        (CACHE / p).write_bytes(data)


VEG_PLEIN = ("BLOC_FEUILLAGE_GRIS", "AB_VEG_ELEV_FEUILLAGE")    # aplats gris (ton par instance), El Croquis 225


class Bibliotheque:
    def __init__(self):
        cat = json.loads((CACHE / "catalogue.json").read_text(encoding="utf-8"))
        self.cat = {b["id"]: b for b in cat["blocs"]}
        base = CACHE / "catalogue_base.json"          # la base est la verite du catalogue (BLOCS-ARCHIBOOKS)
        if base.exists():
            for r in json.loads(base.read_text(encoding="utf-8")):
                if r.get("chemin_dxf") and r["id"] not in self.cat:
                    d = r.get("dimensions") or {}
                    self.cat[r["id"]] = {"id": r["id"], "categorie": r["categorie"], "dxf": r["chemin_dxf"],
                                         "nom_bloc": r["bloc_dxf"], "dimensions_m": {"largeur": d.get("largeur", 1),
                                                                                      "hauteur": d.get("hauteur", 1)}}
        self._sym = {}
        self.utilises = set()

    def info(self, i):
        return self.cat[i]

    def _symbol(self, i):
        if i in self._sym:
            return self._sym[i]
        import ezdxf
        from ezdxf import path as dpath
        b = self.cat[i]
        doc = ezdxf.readfile(CACHE / b["dxf"])
        blk = doc.blocks.get(b["nom_bloc"])
        groups = {}
        tex = b["categorie"] == "texture"
        for e in blk:
            lay = e.dxf.layer
            if tex and lay == "BLOC_CONTOUR":       # variante sans cadre : pas de grille visible en pavage
                continue
            if e.dxftype() == "HATCH":
                paths = list(dpath.from_hatch(e))
                lay = lay if lay in VEG_PLEIN else lay + "#plein"
            elif e.dxftype() == "LWPOLYLINE" and any(p[2] or p[3] for p in e.get_points("xyseb")):
                # polyligne a largeur variable (feuille, palme) : contour reel par TraceBuilder, rendu en aplat
                from ezdxf.render.trace import TraceBuilder
                lay = lay if lay in VEG_PLEIN else lay + "#plein"
                for poly in TraceBuilder.from_polyline(e).polygons():
                    pts = [(v.x, v.y) for v in poly]
                    if len(pts) >= 3:
                        groups.setdefault(lay, []).append("M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z")
                continue
            else:
                try:
                    paths = [dpath.make_path(e)]
                except Exception:
                    continue
            for p in paths:
                pts = list(p.flattening(0.004 if b["categorie"] in ("porte", "personnage") else 0.01))
                if len(pts) < 2:
                    continue
                d = "M" + " L".join(f"{v.x:.3f},{v.y:.3f}" for v in pts) + (" Z" if e.dxftype() == "HATCH" else "")
                groups.setdefault(lay, []).append(d)
        parts = []
        for lay, ds in groups.items():
            if lay in VEG_PLEIN or lay.endswith("#plein"):
                # aplat plein : la teinte vient de l'instance (<use fill=...>) ; tronc en pastille plus sombre
                fill = "" if (lay in VEG_PLEIN or lay.startswith("BLOC_FEUILLAGE")) else ' fill="#4a4a4a"'
                parts.append(f'<path d="{" ".join(ds)}" stroke="none" fill-rule="nonzero"{fill}/>')
                continue
            w, col, fill = STYLE.get(lay, DEF_STYLE)
            if "CONTOUR" in lay and b["categorie"] == "personnage":
                w = 0.6
            op = ' stroke-opacity="0.6"' if ("DETAILS" in lay and b["categorie"] == "personnage") else ""
            parts.append(f'<path d="{" ".join(ds)}" fill="{fill}" stroke="{col}" stroke-width="{w}"{op} '
                         f'vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round"/>')
        sym = f'<g id="ab_{i}">{"".join(parts)}</g>'
        self._sym[i] = sym
        return sym

    def defs(self):
        return "".join(self._symbol(i) for i in sorted(self.utilises))

    # ----------------------------------------------------------------- instances
    def use(self, i, a, b_, c, d, e, f, opacity=1.0, fill=None):
        """Instance par matrice SVG (a b c d e f) appliquee aux coordonnees du bloc (metres, Y haut).
        fill : ton gris de l'instance pour les aplats de vegetation (set_instance_tone)."""
        self.utilises.add(i)
        self._symbol(i)
        f_ = f' fill="{fill}"' if fill else ""
        return (f'<use href="#ab_{i}" transform="matrix({a:.5f},{b_:.5f},{c:.5f},{d:.5f},{e:.2f},{f:.2f})" '
                f'opacity="{opacity}"{f_}/>')

    def plan(self, i, cx, cy, S, k=1.0, rot=0.0, opacity=1.0, X=None, Y=None, fill=None):
        """Bloc vu en plan, centre (cx, cy) en metres du plan (Y vers le Sud) ; S px/m ; k echelle."""
        import math
        r = math.radians(rot)
        a, b_ = k * S * math.cos(r), k * S * math.sin(r)
        c, d = k * S * math.sin(r), -k * S * math.cos(r)      # Y du bloc (Nord) vers le haut de la feuille
        return self.use(i, a, b_, c, d, X(cx), Y(cy), opacity, fill)

    def elevation(self, i, x_px, y_px, S, k=1.0, mirror=False, opacity=1.0, fill=None):
        """Bloc de coupe / elevation (origine au pied), pose en (x_px, y_px) sur la feuille."""
        sx = -k * S if mirror else k * S
        return self.use(i, sx, 0, 0, -k * S, x_px, y_px, opacity, fill)

    def texture(self, i, poly, S, X, Y, opacity=0.6, holes=(), cid=None, rot=0.0):
        """Recouvre un polygone (metres du plan) de panneaux 2 x 2 m, recadres exactement (clipPath, trous)."""
        self.utilises.add(i)
        self._symbol(i)
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        cid = cid or f"clip_{i}_{abs(hash((tuple(poly), tuple(map(tuple, holes))))) % 10**8}"
        dpoly = "M" + " L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in poly) + " Z"
        for h in holes:
            dpoly += " M" + " L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in h) + " Z"
        out = [f'<clipPath id="{cid}"><path d="{dpoly}" clip-rule="evenodd"/></clipPath><g clip-path="url(#{cid})" opacity="{opacity}">']
        x = (min(xs) // 2) * 2
        while x < max(xs):
            y = (min(ys) // 2) * 2
            while y < max(ys):
                # panneau : origine bas-gauche ; en plan, Y du bloc vers le Nord
                out.append(f'<use href="#ab_{i}" transform="matrix({S:.4f},0,0,{-S:.4f},{X(x):.2f},{Y(y + 2):.2f})"/>')
                y += 2
            x += 2
        out.append("</g>")
        return "".join(out)


def porte_matrix(x, y, sens, w, swing, hinge_low, S, X, Y):
    """Matrice d'une porte Archibooks (gond a l'origine, mur entre v=0 et v=0,20, ouverture vers +v).

    (x, y, sens, w) : porte du modele (centre sur la ligne du mur) ; swing = +1 ouvre vers les x / y croissants ;
    hinge_low = gond du cote des faibles coordonnees. Echelle = largeur / 0,90 (porte simple) ou / 1,40 (double)."""
    k = w / (0.90 if w < 1.15 else 1.40)
    if sens == "h":
        eu = (1.0, 0.0) if hinge_low else (-1.0, 0.0)
        ev = (0.0, float(swing))
        hx, hy = (x - w / 2, y) if hinge_low else (x + w / 2, y)
    else:
        eu = (0.0, 1.0) if hinge_low else (0.0, -1.0)
        ev = (float(swing), 0.0)
        hx, hy = (x, y - w / 2) if hinge_low else (x, y + w / 2)
    # le mur du bloc (v de 0 a 0,20 x k) est centre sur la ligne du modele
    ox, oy = hx - ev[0] * 0.10 * k, hy - ev[1] * 0.10 * k
    a, b_ = eu[0] * k * S, eu[1] * k * S
    c, d = ev[0] * k * S, ev[1] * k * S
    # miroir si le repere (eu, ev) est indirect : le bloc reste lisible (pas de symetrie parasite)
    return a, b_, c, d, X(ox), Y(oy)
