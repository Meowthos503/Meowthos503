from pathlib import Path
import json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
W,H=80,66
C=dict(out='#131822',fur='#242633',body='#2C2E3E',shade='#1C202B',hi='#3C3C50',soft='#4F4B63',pink='#DCA0B3',ear='#8E789F',gold='#E9C579',blue='#8DBED1',glint='#FFF4D4',toy='#B39BCD',toyHi='#E5D8EB')
def layer():return Image.new('RGBA',(W,H),(0,0,0,0))
def draw_mask(shape,color='fur',outline=True):
 m=Image.new('1',(W,H));d=ImageDraw.Draw(m);shape(d)
 im=layer();p=im.load();mp=m.load()
 for y in range(H):
  for x in range(W):
   if mp[x,y]:p[x,y]=(*tuple(bytes.fromhex(C[color][1:])),255)
   elif outline and any(0<=x+dx<W and 0<=y+dy<H and mp[x+dx,y+dy] for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))):p[x,y]=(*tuple(bytes.fromhex(C['out'][1:])),255)
 return im

def ellipse_mask(box,col='fur'):
 return draw_mask(lambda d:d.ellipse(box,fill=1),col)
def rect(d,box,col):d.rectangle(box,fill=C[col])
def face(center=(40,27), expression='open',look=0,ear=0,squash=0):
 cx,cy=center
 flat=max(squash,3 if expression in ('closed','wink') else 0)
 # Two small ears grow out of a broad cheek-heavy head. This art is original.
 im=draw_mask(lambda d:(d.polygon([(cx-17,cy-8+flat),(cx-17-ear,cy-20+flat),(cx-8,cy-16+flat),(cx+8,cy-16+flat),(cx+17+ear,cy-20+flat),(cx+17,cy-8+flat)],fill=1),d.ellipse((cx-21,cy-15+flat,cx+21,cy+14-flat),fill=1)))
 d=ImageDraw.Draw(im)
 d.polygon([(cx-15,cy-10+flat),(cx-15-ear,cy-16+flat),(cx-9,cy-13+flat)],fill=C['ear'])
 d.polygon([(cx+9,cy-13+flat),(cx+15+ear,cy-16+flat),(cx+15,cy-10+flat)],fill=C['ear'])
 # Soft forehead/fur highlights are broad, never a robotic frame.
 rect(d,(cx-11,cy-11,cx-7,cy-10),'hi');rect(d,(cx-5,cy-12,cx-2,cy-11),'hi');rect(d,(cx-20,cy-3,cx-20,cy+1),'soft')
 for ex,col in ((cx-10,'gold'),(cx+10,'blue')):
  this_expression='open' if expression=='wink' and col=='gold' else 'closed' if expression=='wink' else expression
  if this_expression=='closed':
   d.line([(ex-4,cy+1),(ex-3,cy+3),(ex+2,cy+3),(ex+4,cy+1)],fill=C['soft'],width=1)
  elif this_expression=='blink':d.line([(ex-4,cy+3),(ex+4,cy+3)],fill=C['gold'] if col=='gold' else C['blue'],width=1)
  else:
   d.ellipse((ex-4,cy-2,ex+4,cy+5),fill=C[col]);d.rectangle((ex+look-1,cy-2,ex+look,cy+5),fill=C['shade']);rect(d,(ex+2,cy-1,ex+3,cy),'glint')
   if this_expression=='half':rect(d,(ex-4,cy-2,ex+4,cy+1),'fur')
 rect(d,(cx-1,cy+7,cx+1,cy+7),'pink');rect(d,(cx,cy+8,cx,cy+9),'soft');rect(d,(cx-3,cy+10,cx-1,cy+10),'soft');rect(d,(cx+1,cy+10,cx+3,cy+10),'soft')
 rect(d,(cx-17,cy+7,cx-14,cy+7),'hi');rect(d,(cx+14,cy+7,cx+17,cy+7),'hi')
 return im

def pose(kind='loaf',expr='open',look=0,ear=0,paw=0,stretch=0,bob=0,tail=0):
 im=layer()
 if kind=='sleep':
  # Hips curl around the resting head; the tail follows the mound.
  im.alpha_composite(ellipse_mask((17,30-bob,67,58),'body'))
  t=draw_mask(lambda d:d.line([(62,47),(68,43),(69,50),(65,58),(45,60),(33,58)],fill=1,width=5),'fur');im.alpha_composite(t)
  im.alpha_composite(face((32,46),'closed',0,-1));d=ImageDraw.Draw(im)
  rect(d,(22,58,29,61),'fur');rect(d,(22,61,29,61),'hi');rect(d,(52,33-bob,57,34-bob),'hi')
 elif kind=='stretch':
  # Hips remain high, chest descends, front paws slide forward along the floor.
  im.alpha_composite(draw_mask(lambda d:d.line([(64,43),(69,34),(69,20),(66,15)],fill=1,width=5),'body'))
  im.alpha_composite(draw_mask(lambda d:(d.ellipse((37,29,66,55),fill=1),d.polygon([(43,41),(35,49),(23-stretch,56),(19-stretch,61),(39,61),(49,49)],fill=1)),'body'))
  im.alpha_composite(ellipse_mask((17-stretch,56,33-stretch,62),'fur'))
  im.alpha_composite(ellipse_mask((40-stretch,56,53-stretch,62),'fur'))
  im.alpha_composite(face((30-stretch//2,43+bob),expr,look,ear));d=ImageDraw.Draw(im);rect(d,(20-stretch,62,24-stretch,62),'hi');rect(d,(43-stretch,62,47-stretch,62),'hi')
 else:
  # Tail curls behind the loaf, and head overlaps a low torso throughout.
  im.alpha_composite(draw_mask(lambda d:(d.line([(61,50),(69,48),(72,42-tail),(71,37-tail),(67,35-tail),(64,37-tail)],fill=1,width=5),d.ellipse((62,35-tail,66,39-tail),fill=1)),'body'))
  im.alpha_composite(ellipse_mask((17,37,64,59),'body'))
  if paw:
   im.alpha_composite(draw_mask(lambda d:d.polygon([(29,50),(32,56),(29-paw,60),(21-paw,58)],fill=1),'body'))
  im.alpha_composite(draw_mask(lambda d:d.ellipse((21-paw,56,33-paw,61),fill=1),'body',False));im.alpha_composite(draw_mask(lambda d:d.ellipse((45,56,57,61),fill=1),'body',False))
  im.alpha_composite(face((40,29+bob),expr,look,ear));d=ImageDraw.Draw(im)
  rect(d,(24-paw,61,29-paw,61),'hi');rect(d,(48,61,53,61),'hi');rect(d,(56,43,59,44),'hi');rect(d,(18,44,18,48),'soft');rect(d,(72,40-tail,72,43-tail),'soft')
 return im

def lerp(a,b,f):return round(a+(b-a)*f)
def morph(kind,f,expr='closed'):
 im=layer()
 if kind=='stretch':
  tail0=[(61,50),(69,48),(73,42),(72,37),(67,35),(64,37)]
  tail1=[(61,48),(67,40),(69,30),(69,20),(66,15),(66,15)]
  pts=[(lerp(a,c,f),lerp(b,d,f)) for (a,b),(c,d) in zip(tail0,tail1)]
  im.alpha_composite(draw_mask(lambda d:d.line(pts,fill=1,width=5),'body'))
  box=tuple(lerp(a,b,f) for a,b in zip((17,37,64,59),(37,29,66,55)))
  im.alpha_composite(ellipse_mask(box,'body'))
  fore0=[(30,43),(44,43),(35,58),(22,58)];fore1=[(49,41),(49,49),(22,61),(13,61)]
  fg=[(lerp(a,c,f),lerp(b,d,f)) for (a,b),(c,d) in zip(fore0,fore1)]
  im.alpha_composite(draw_mask(lambda d:d.polygon(fg,fill=1),'body'))
  for a,b in [((21,56,33,61),(13,57,29,62)),((45,56,57,61),(36,57,49,62))]:
   im.alpha_composite(ellipse_mask(tuple(lerp(x,y,f) for x,y in zip(a,b))))
  im.alpha_composite(face((lerp(40,28,f),lerp(29,43,f)),expr))
 elif kind=='curl':
  im.alpha_composite(ellipse_mask(tuple(lerp(a,b,f) for a,b in zip((17,37,64,59),(17,30,67,58))),'body'))
  tail0=[(61,50),(69,48),(73,42),(72,37),(67,35),(64,37)]
  tail1=[(62,47),(68,43),(69,50),(65,58),(45,60),(33,58)]
  pts=[(lerp(a,c,f),lerp(b,d,f)) for (a,b),(c,d) in zip(tail0,tail1)]
  im.alpha_composite(draw_mask(lambda d:d.line(pts,fill=1,width=5),'fur'))
  im.alpha_composite(ellipse_mask(tuple(lerp(a,b,f) for a,b in zip((21,56,33,61),(22,58,30,61)))))
  im.alpha_composite(ellipse_mask(tuple(lerp(a,b,f) for a,b in zip((45,56,57,61),(45,54,57,59)))))
  im.alpha_composite(face((lerp(40,32,f),lerp(29,46,f)),expr,0,-1))
 return im

def shapes(im):
 # Every filled path is composed of horizontal pixel runs, with no bitmap links.
 colors={};p=im.load()
 for y in range(H):
  x=0
  while x<W:
   c=p[x,y]
   if c[3]==0:x+=1;continue
   x2=x+1
   while x2<W and p[x2,y]==c:x2+=1
   colors.setdefault('#%02X%02X%02X'%c[:3],[]).append(f'M{x} {y}h{x2-x}v1h-{x2-x}Z');x=x2
 return ''.join(f'<path fill="{c}" d="{"".join(ds)}"/>' for c,ds in colors.items())

# Named poses are reused across a slow, comprehensible state machine.
POSES={
'loaf':pose(), 'blink':pose(expr='blink'), 'half':pose(expr='half'),
'listen':pose(look=-1,ear=1,tail=1), 'watch':pose(look=-2,ear=1),
'reach2':pose(look=-2,paw=2), 'reach5':pose(look=-2,paw=5), 'reach8':pose(look=-2,paw=8), 'reach11':pose(look=-2,paw=11),
'sleep':pose('sleep'), 'breathe':pose('sleep',bob=1), 'wink':morph('curl',1,'wink'),
'wakehalf':pose(expr='half',bob=1), 'wake':pose(bob=1,ear=1)
}
for i in range(1,7):
 POSES['stretch'+str(i)]=morph('stretch',i/6)
 POSES['curl'+str(i)]=morph('curl',i/6)
# Morph at 7–10 pixel poses per second during transitions, hold for the actions.
TIMELINE=[(0,'loaf'),(2.4,'blink'),(2.55,'loaf'),(4.2,'listen'),(5.4,'watch'),(6.0,'reach2'),(6.15,'reach5'),(6.3,'reach8'),(6.45,'reach11'),(6.8,'reach8'),(6.95,'reach5'),(7.1,'reach2'),(7.25,'watch'),(8.4,'loaf'),(10.3,'half')]
TIMELINE += [(11+i*.13,'stretch'+str(i)) for i in range(1,7)]
TIMELINE += [(12.9+(6-i)*.13,'stretch'+str(i)) for i in range(6,0,-1)]
TIMELINE += [(13.68,'half')]
TIMELINE += [(14+i*.14,'curl'+str(i)) for i in range(1,7)]
TIMELINE += [(15.0,'sleep'),(16.0,'breathe'),(17.2,'sleep'),(18.6,'breathe'),(19.8,'sleep'),(21.2,'breathe'),(22.4,'sleep'),(23.5,'wink')]
TIMELINE += [(24+(6-i)*.14,'curl'+str(i)) for i in range(6,0,-1)]
TIMELINE += [(24.9,'wakehalf'),(25.4,'wake'),(26.0,'loaf'),(27.1,'blink'),(27.25,'loaf'),(30.0,'loaf')]
TIMELINE.sort()
# The light block rocks on its weighted base and settles; no unexplained return.
TOY=[(0,0,0,0),(6.44,0,0,0),(6.45,0,0,-12),(6.6,0,0,-24),(6.75,0,0,-8),(6.9,0,0,8),(7.05,0,0,-4),(7.2,0,0,2),(7.4,0,0,0),(30.0,0,0,0)]

def state(t):
 at=TIMELINE[0][1]
 for s,v in TIMELINE:
  if t>=s:at=v
 return at
def toy(t):
 at=TOY[0][1:]
 for s,*v in TOY:
  if t>=s:at=v
 return at

def css():
 lines=[]
 for name in POSES:
  pts=[];prev=None
  for t,v in TIMELINE:
   val=int(v==name)
   if val!=prev or t==30:pts.append(f'{t/30*100:.8f}%{{opacity:{val}}}');prev=val
  lines.append('@keyframes pose-'+name+'{'+''.join(pts)+'}'+'.pose-'+name+'{animation:pose-'+name+' 30s steps(1,end) infinite}')
 lines.append('@keyframes toy{'+''.join(f'{t/30*100:.8f}%{{transform:translate({x}px,{y}px) rotate({r}deg)}}' for t,x,y,r in TOY)+'}.toy{transform-origin:12px 59px;animation:toy 30s steps(1,end) infinite}')
 lines.append('@media(prefers-reduced-motion:reduce){.cat-pose,.toy{animation:none!important}.cat-pose{opacity:0!important}.pose-loaf{opacity:1!important}}')
 return '\n'.join(lines)

PAL={'light':dict(bg='#F3EEDD',edge='#D4C9CF',cushion='#D8D0E1',base='#A7A0B9'), 'dark':dict(bg='#51435D',edge='#695971',cushion='#695D7A',base='#8A759B')}
def svg(theme='light',motion=True,t=None):
 p=PAL[theme];out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 510" width="900" height="510" role="img" aria-labelledby="cat-title cat-desc">', '<title id="cat-title">Meowthos · 小猫歇一会儿</title>','<desc id="cat-desc">Original charcoal pixel kitten with a broad round head, gold and blue eyes and short paws. It rests, blinks, listens, gently bats a little block, stretches, curls up to sleep and wakes in a thirty-second loop. Use the surrounding native fold control to hide the animation; a still companion is offered for reduced motion. This image is not interactive.</desc>']
 if motion and t is None:out+=['<style>',css(),'</style>']
 out+=['<g shape-rendering="crispEdges">',f'<path fill="{p["bg"]}" d="M0 0H900V510H0Z"/>',f'<path fill="{p["edge"]}" d="M230 451H690V455H230Z"/>',f'<path fill="{p["base"]}" d="M278 420H635V447H278Z"/>',f'<path fill="{p["cushion"]}" d="M266 418H645V435H266Z M282 410H628V441H282Z"/>','<g transform="translate(175 16) scale(7)">']
 tx,ty,tr=toy(0 if t is None else t)
 out+=[f'<g class="toy" transform="translate({tx} {ty}) rotate({tr} 12 59)">',f'<path fill="{C["toy"]}" d="M9 53H15V59H9Z"/>',f'<path fill="{C["toyHi"]}" d="M9 53H15V54H9Z M9 54H10V57H9Z"/>','</g>']
 selected=state(0 if t is None else t)
 for name,im in POSES.items():
  if t is not None or not motion:
   if name!=selected:continue
   out.append(shapes(im))
  else:out.append(f'<g class="cat-pose pose-{name}" opacity="{int(name=="loaf")}">{shapes(im)}</g>')
 out+=['</g>','</g>','</svg>'];return '\n'.join(out)+'\n'
if __name__=='__main__':
 for theme in PAL:
  for motion in (True,False):
   name='cat-'+theme+('' if motion else '-static')+'.svg'
   (R/'assets'/name).write_text(svg(theme,motion),encoding='utf-8')
 print('Built four original pixel-cat SVG companions')
