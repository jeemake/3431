"""Images d'ambiance (IA) via fal.ai — usage illustratif uniquement."""
import json, subprocess, sys, os, concurrent.futures as cf
OUT = os.path.join(os.path.dirname(__file__), '..', 'img')
COMMON = ("photorealistic architectural visualization, West African coastal town of Jacqueville Ivory Coast, "
          "humid tropical climate, lush native vegetation, coconut palms, Terminalia catappa trees, white sand soil, "
          "earth-brick openwork claustra, solid iroko timber posts, light lime render, soft golden hour light, no text, no logo")
PROMPTS = {
 'B_village': "eye-level view from a garden lawn toward three separate slender three-storey tower houses standing side by side with 3 m gaps between them, "
              "each tower 9 m wide with stacked rooms, deep timber loggias with vertical iroko louvres, earth-brick openwork gable wall, "
              "and a single tall steep four-sided pyramid roof in synthetic thatch on timber posts with wide eaves, external timber stairs in the gaps, "
              "palms growing in the gaps, small natural grass football lawn with two small white goals in the foreground, a few kids playing. " + COMMON,
 'B_case':    "open-air restaurant pavilion under two adjoining tall pyramidal thatched roofs on massive timber posts, ceiling fans, rattan chairs, "
              "opening onto a natural grass lawn and a narrow lap pool, slender tower houses with thatched roofs behind, evening light. " + COMMON,
 'A_aerien': "aerial 3/4 view of a slender three-storey boutique hotel bar oriented east-west on a small 40m plot, "
             "rooftop with a fenced five-a-side football cage with green turf and nets next to an open-air thatched-roof rooftop restaurant, "
             "deep timber loggias with vertical louvers on south facade, climbing plants on gable walls, large tropical garden in front "
             "with a long narrow lap pool, low-rise neighbourhood, Atlantic ocean visible 300 m away on the horizon. " + COMMON,
 'A_toit':   "eye-level view on a hotel rooftop at sunset: small football cage with green artificial turf and black nets, "
             "players in silhouette, next to it a bar-restaurant under a large thatched roof on timber columns, string lights, "
             "Atlantic ocean and palm canopy on the horizon. " + COMMON,
 'A_jardin': "ground-level view in a hotel garden: long narrow lap pool with timber deck and a small cold plunge bath, "
             "three-storey building behind with deep shaded loggias, timber louvers, earth-brick claustra and vertical gardens, "
             "dense tropical planting, hammocks under trees. " + COMMON,
 'B_aerien': "aerial 3/4 view of a tiny boutique eco-hotel village: three slender three-storey tower-houses with tall steep pyramidal thatched roofs "
             "on timber posts, staggered around a natural grass lawn used as a small football pitch with two small goals, "
             "an open common pavilion with twin pyramidal thatched roofs for reception and restaurant, winding sand paths, planted mounds, "
             "small lap pool, low-rise neighbourhood. " + COMMON,
 'B_pelouse':"eye-level view of a natural grass lawn small football pitch in a tropical hotel garden, children and an adult playing, "
             "slender three-storey tower-houses with steep thatched roofs, timber galleries and earth-brick claustra around, palms. " + COMMON,
 'chambre':  "interior of a hotel room in a tropical eco-hotel: timber ceiling, ceiling fan, full-height sliding timber shutters open to a deep loggia "
             "and garden canopy, high clerestory for cross ventilation, terrazzo floor, woven rattan furniture, linen bed, calm. " + COMMON,
}
def gen(item):
    k, p = item
    body = json.dumps({"prompt": p, "image_size": "landscape_16_9", "num_images": 1, "safety_tolerance": "2"})
    r = subprocess.run(['curl','-sS','-m','300','-X','POST','https://fal.run/fal-ai/flux-pro/v1.1',
                        '-H','Authorization: Key dummy','-H','Content-Type: application/json','-d',body],
                       capture_output=True, text=True)
    try:
        url = json.loads(r.stdout)['images'][0]['url']
    except Exception:
        return k, 'ERR ' + r.stdout[:300]
    subprocess.run(['curl','-sS','-o',os.path.join(OUT, k + '.jpg'), url])
    return k, 'ok'
keys = sys.argv[1:] or list(PROMPTS)
with cf.ThreadPoolExecutor(6) as ex:
    for k, s in ex.map(gen, [(k, PROMPTS[k]) for k in keys]):
        print(k, s)
