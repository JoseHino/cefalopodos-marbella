# Sustituye el mapa de la infografía por uno real: término de Marbella + línea de base recta (RD 2510/1977)
import json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D='C:/Users/josem/dev/cefalopodos-marbella/'
S=3                                  # supermuestreo
X0,Y0,X1,Y1=25,823,1335,1288         # interior del recuadro del mapa
W,H=(X1-X0)*S,(Y1-Y0)*S
lon0,lon1=-5.045,-4.672
k=math.cos(math.radians(36.48))
lat_span=(lon1-lon0)*k*H/W
lat1=36.545; lat0=lat1-lat_span
px=lambda lo,la:((lo-lon0)/(lon1-lon0)*W,(lat1-la)/(lat1-lat0)*H)
NAVY=(7,36,80); RED=(158,25,20); PINK=(236,178,172); SEA=(118,187,216); LINE=(8,74,152)
LAND=(232,218,196); LAND_MB=(242,232,212); EDGE=(190,170,140)
F='C:/Windows/Fonts/bahnschrift.ttf'
def font(sz,var=b'Bold Condensed'):
    f=ImageFont.truetype(F,sz*S)
    try: f.set_variation_by_name(var)
    except Exception: pass
    return f
ring=json.load(open(D+'fuente/termino.geojson',encoding='utf-8')); ring=(ring['features'][0] if 'features' in ring else ring)['geometry']['coordinates'][0]
# línea de base recta (BOE): Pta. Carbonera, Pta. de Baños, Torre de Calahonda, Pta. Calaburras
carb=(-5.30,36.245); banos=(-5.0058,36.4602); calah=(-4.71,36.4887); calab=(-4.6383,36.5083)
def at(a,b,lo): return a[1]+(lo-a[0])/(b[0]-a[0])*(b[1]-a[1])
base=[(lon0-0.01,at(carb,banos,lon0-0.01)),banos,calah,calab]
# costa de Marbella = puntos del término sin ningún otro borde del término al sur
def crossings(p):
    n=0
    for a,b in zip(ring,ring[1:]):
        if a==p or b==p: continue
        if (a[0]-p[0])*(b[0]-p[0])<0:
            y=a[1]+(p[0]-a[0])/(b[0]-a[0])*(b[1]-a[1])
            if y<p[1]: n+=1
    return n
coast=sorted({tuple(p) for p in ring if crossings(p)==0 and p[1]<36.52 and -5.0050<=p[0]<=-4.7389})
wc=[(lon0-0.01,36.447),(-5.03,36.452)]
ec=[(-4.71,36.4887),(-4.69,36.4905),(lon1+0.01,36.494)]
full=wc+coast+ec
img=Image.new('RGB',(W,H),SEA); d=ImageDraw.Draw(img)
# aguas interiores: todo lo que queda por encima de la línea de base
d.polygon([px(*p) for p in base]+[px(lon1+0.01,at(calah,calab,lon1+0.01)),px(lon1+0.01,lat1+0.05),px(lon0-0.01,lat1+0.05)],fill=PINK)
# tierra
d.polygon([px(*p) for p in full]+[px(lon1+0.01,lat1+0.05),px(lon0-0.01,lat1+0.05)],fill=LAND)
d.polygon([px(*p) for p in ring],fill=LAND_MB,outline=EDGE)
d.line([px(*p) for p in ring],fill=(150,120,90),width=2*S)
d.line([px(*p) for p in full],fill=EDGE,width=2*S)
# línea de base discontinua
def dashed(pts,dash=26*S,gap=16*S,w=6*S):
    acc=0;on=True
    for (ax,ay),(bx,by) in zip(pts,pts[1:]):
        L=math.hypot(bx-ax,by-ay);t=0
        while t<L:
            step=min((dash if on else gap)-acc,L-t)
            if on: d.line([(ax+(bx-ax)*t/L,ay+(by-ay)*t/L),(ax+(bx-ax)*(t+step)/L,ay+(by-ay)*(t+step)/L)],fill=LINE,width=w)
            t+=step;acc+=step
            if acc>=(dash if on else gap): acc=0;on=not on
dashed([px(*p) for p in base])
def text(xy,s,f,fill,anchor='mm',stroke=0,sf=None):
    d.text(xy,s,font=f,fill=fill,anchor=anchor,stroke_width=stroke*S,stroke_fill=sf)
# extremos de la línea
for n,p,dx,dy,an in [('Punta de Baños',banos,0,30,'mt'),('Torre de Calahonda',calah,0,30,'mt')]:
    x,y=px(*p); r=9*S; d.ellipse([x-r,y-r,x+r,y+r],fill=LINE,outline='white',width=3*S)
    text((x+dx*S,y+dy*S),n,font(27),LINE,an,5,(255,255,255))
# localidades
f=font(26,b'SemiBold Condensed')
for n,lo,la,an,dx,dy in [('San Pedro',-4.99,36.476,'mb',0,-20),('Puerto Banús',-4.953,36.485,'mb',0,-20),('Marbella',-4.886,36.508,'mb',0,-20),('Elviria',-4.79,36.493,'mb',0,-20),('Cabopino',-4.745,36.489,'mb',0,-20)]:
    x,y=px(lo,la); r=6*S; d.ellipse([x-r,y-r,x+r,y+r],fill=NAVY)
    text((x+dx*S,y+dy*S),n,f,NAVY,an,3,LAND_MB)
text((W*0.5,32*S),'TÉRMINO MUNICIPAL DE MARBELLA',font(46),NAVY,'mt',6,LAND_MB)
# cotas: puerto de Marbella y Puerto Banús
for lo,la,lab,lado in [(-4.886,36.5065,'aprox. 4 km',-1),(-4.953,36.4835,'aprox. 2 km',1)]:
    x,y1=px(lo,la); _,y2=px(lo,at(banos,calah,lo))
    d.line([(x,y1+12*S),(x,y2-12*S)],fill=NAVY,width=4*S)
    for yy,sg in [(y1+8*S,1),(y2-8*S,-1)]:
        d.polygon([(x,yy),(x-9*S,yy+16*S*sg),(x+9*S,yy+16*S*sg)],fill=NAVY)
    text((x+14*S*lado,(y1+y2)/2),lab,font(30),NAVY,'lm' if lado>0 else 'rm',4,PINK)
# rótulos de zonas
text(px(-4.828,36.4915),'AGUAS INTERIORES',font(31),RED,'mm',4,PINK)
text(px(-4.828,36.4850),'JUNTA DE ANDALUCÍA',font(31),RED,'mm',4,PINK)
text(px(-5.03,36.47),'Estepona',font(24,b'SemiBold Condensed'),(120,105,85),'mm')
text(px(-4.70,36.50),'Mijas',font(24,b'SemiBold Condensed'),(120,105,85),'mm')
text(px(-4.84,36.452)[0:1]+(px(0,36.452)[1],),'AGUAS EXTERIORES · ESTADO',font(40),NAVY,'mm')
text((W-16*S,H-14*S),'Línea de base recta · RD 2510/1977',font(22,b'SemiBold Condensed'),LINE,'rb')
mapa=img.resize((X1-X0,Y1-Y0),Image.LANCZOS)
base_img=Image.open(D+'fuente/infografia_original.jpg').convert('RGB')
mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,W-1,H-1],radius=14*S,fill=255)
mask=mask.resize(mapa.size,Image.LANCZOS)
base_img.paste(mapa,(X0,Y0),mask)
base_img.save(D+'infografia.jpg',quality=88,optimize=True)
base_img.crop((0,790,1360,1320)).save(D+'../_tmp_cef/nuevo_mapa.png')
print('ok', lat0, lat1)
