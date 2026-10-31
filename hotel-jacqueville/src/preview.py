import sys
from geo import *
from svgkit import Sheet, en
from shapely.geometry import box
pts=[en(*c) for c in SITE.exterior.coords]
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
s=Sheet(min(xs)-3,min(ys)-3,max(xs)+3,max(ys)+3,scale=18)
s.poly(SITE,fill='#eef3e6',sw=1.5)
s.poly(buildable(),fill='none',stroke='#c55',dash='4 3')
f,_=bar_frame()
shapes=eval(sys.argv[1])
for n,(u0,v0,w,d) in shapes.items():
    r=rect_uv(u0,v0,u0+w,v0+d); ok=buildable().buffer(1e-6).contains(r)
    s.poly(r,fill='#d9c6a5' if ok else '#f99',stroke='#333'); c=r.centroid; s.text(c.x,c.y,n,12)
for u in range(0,41,5):
    a=f(u,0); s.text(a[0],a[1],'u%d'%u,8)
for v in range(0,31,5):
    a=f(0,v); s.text(a[0],a[1],'v%d'%v,8)
open('/tmp/claude-0/-home-user-3431/4f30e584-ab62-54e8-8eab-c4cbf97c8741/scratchpad/prev.svg','w').write(s.svg())
