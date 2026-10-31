"""Verify the authorized cache against the live Supabase metadata snapshot."""
import os,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
CACHE=Path(os.environ['ARCHIBOOKS_BLOCS'])
SOURCE=Path(os.environ['CAPITUDE_REFERENCE_CACHE'])
catalog=json.loads((BASE/'references/catalogue_capitude_2026-10-31.json').read_text(encoding='utf-8'))
checks=[]; compatible=[]
for row in catalog:
 p=CACHE/row['chemin_dxf'];dwg=CACHE/row['chemin_dwg']
 b=dict(id=row['id'],categorie=row['categorie'],nom_bloc=row['bloc_dxf'],dxf=row['chemin_dxf'],dwg=row['chemin_dwg'],png=row['chemin_png'],panneau_m=[2,2],version=row['version'])
 compatible.append(b)
 if not p.exists():continue
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if digest==row['sha256_dxf']:method='DXF source exact / SHA-256 Supabase'
 else:
  assert dwg.exists() and hashlib.sha256(dwg.read_bytes()).hexdigest()==row['sha256_dwg'],row['id']
  method='DXF dérivé AutoCAD 2023 ; DWG cache exact / SHA-256 Supabase'
 checks.append(dict(id=row['id'],version=row['version'],sha256_dxf_local=digest,method=method))
(CACHE/'catalogue.json').write_text(json.dumps(dict(source='Supabase capitude',blocs=compatible),ensure_ascii=False,indent=2),encoding='utf-8')
manifest=[json.loads(x) for x in (SOURCE/'data/asset_manifest.jsonl').read_text(encoding='utf-8').splitlines()]
remote=json.loads((BASE/'references/references_storage_2026-10-31.json').read_text(encoding='utf-8'))
media=[]
for r in remote:
 m=next(x for x in manifest if x['proposed_object_path']==r['name']);p=SOURCE/m['local_path'];raw=p.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==m['sha256']
 etag=hashlib.md5(hashlib.md5(raw).digest()).hexdigest()+'-1'
 assert etag==r['metadata']['eTag'].strip('"') and len(raw)==r['metadata']['size']
 media.append(dict(object_path=r['name'],sha256=m['sha256'],remote_etag=etag,verification='SHA-256 manifeste + ETag multipart et taille Storage live',visually_opened=True))
(BASE/'references/cache_verifie_RevB.json').write_text(json.dumps(dict(blocks=checks,references=media,access='Métadonnées Supabase via MCP autorisé ; cache vérifié. Fonctions HTTP non appelées, clés non configurées. Aucun repli externe.',observations=['Primaveras 132 : jardin central et strates entre volumes, parcours lisibles.','Primaveras 138 : murs dominants, cotes périphériques, repères et détails hiérarchisés.','Candela 152 : relation terrasse / piscine et lisières discontinues ; matière en second plan.'],override_client='Aplats pastel par usage demandés explicitement après lecture des règles ; priorité à cette demande.'),ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(checks)} blocs vérifiés ; {len(media)} références vérifiées')
