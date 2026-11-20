"""Hitman DevOps — Kubernetes promo: animated infographic video. Usage: python3 make.py W H out.mp4"""
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont
W,H,OUT=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
FPS=30; F="/usr/share/fonts/truetype/dejavu/"
U=min(W,H)/1080; V=H>W
def font(n,s): return ImageFont.truetype(F+n,int(s*U))
B=lambda s:font("DejaVuSans-Bold.ttf",s); R=lambda s:font("DejaVuSans.ttf",s); M=lambda s:font("DejaVuSansMono.ttf",s)
BG=(10,14,22); GRID=(18,26,38); RED=(232,44,64); WHITE=(255,255,255); GREY=(150,165,185); GREEN=(70,220,140); PANEL=(22,30,44); BLUE=(70,150,255)
SITE="aidyn.stream"; NAME="HITMAN DEVOPS"
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","voice.mp3"]))
T=json.load(open("timing.json"))+[dur+1.5]; TOTAL=T[-1]
ease=lambda x:1-(1-max(0,min(1,x)))**3
def lerp(a,b,k): return tuple(int(a[i]+(b[i]-a[i])*k) for i in range(3))
CW=min(W*0.86,1500*U); X0=(W-CW)/2
TOP=H*0.20 if V else H*0.17  # title y
GY=H*0.40 if V else H*0.42   # graphic top
GH=H*0.42 if V else H*0.44   # graphic height

def ctext(d,y,s,f,c,x=None):
    w=d.textlength(s,font=f); d.text(((W-w)/2 if x is None else x,y),s,font=f,fill=c)
def crosshair(d,cx,cy,r,ang,c=RED,wd=6):
    wd=max(2,int(wd*U))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=c,width=wd); d.ellipse([cx-r*.45,cy-r*.45,cx+r*.45,cy+r*.45],outline=c,width=wd)
    for k in range(4):
        a=ang+k*math.pi/2; d.line([cx+math.cos(a)*r*.6,cy+math.sin(a)*r*.6,cx+math.cos(a)*r*1.25,cy+math.sin(a)*r*1.25],fill=c,width=wd)
    d.ellipse([cx-r*.1,cy-r*.1,cx+r*.1,cy+r*.1],fill=c)
def title(d,t,head,sub):
    k=ease(t/0.6); y=TOP+(1-k)*40*U; c=lerp(BG,WHITE,k)
    f=B(84 if V else 80)
    while d.textlength(head,font=f)>CW: f=B(f.size/U-4)
    ctext(d,y,head,f,c); ctext(d,y+110*U,sub,R(40 if V else 38),lerp(BG,GREY,k))

def hexagon(d,cx,cy,r,fill=None,outline=None,w=3):
    pts=[(cx+r*math.cos(math.pi/6+k*math.pi/3),cy+r*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
    d.polygon(pts,fill=fill,outline=outline,width=max(1,int(w*U)))
def pod(d,x,y,s,col):
    d.rounded_rectangle([x,y,x+s,y+s],int(s*0.2),fill=col)
    hexagon(d,x+s/2,y+s/2,s*0.25,fill=BG)

def s_intro(d,t,L):
    cy=H*0.38
    for k in range(7):
        a=k*math.pi/3+t*0.4; rr=0 if k==6 else 120*U
        kk=ease((t-k*0.12)/0.5)
        if kk>0: hexagon(d,W/2+math.cos(a)*rr*kk,cy+math.sin(a)*rr*kk,62*U*kk,fill=RED if k==6 else BLUE)
    n=int(len(NAME)*min(1,max(0,(t-0.6)/1.0))); ctext(d,cy+230*U,NAME[:n],B(96 if V else 100),WHITE)
    k2=ease((t-1.6)/0.6); ctext(d,cy+350*U,"Kubernetes без головной боли",R(40),lerp(BG,GREY,k2))
    tags=["Pods","Helm","HPA","GitOps"]; f=M(30); gap=24*U
    ws=[d.textlength(s,font=f)+40*U for s in tags]
    rows=[tags[:2],tags[2:]] if V else [tags]; y=cy+440*U; i=0
    for row in rows:
        tw=sum(ws[i:i+len(row)])+gap*(len(row)-1); x=(W-tw)/2
        for s in row:
            kk=ease((t-2.2-i*0.25)/0.4)
            if kk>0:
                d.rounded_rectangle([x,y,x+ws[i],y+56*U],int(28*U),outline=lerp(BG,RED,kk),width=max(2,int(3*U)))
                d.text((x+20*U,y+10*U),s,font=f,fill=lerp(BG,WHITE,kk))
            x+=ws[i]+gap; i+=1
        y+=80*U

def s_arch(d,t,L):
    title(d,t,"Архитектура кластера","Control plane · ноды · сеть · хранилище")
    cph=110*U; k=ease((t-0.4)/0.6)
    d.rounded_rectangle([X0,GY,X0+CW,GY+cph],int(16*U),fill=PANEL,outline=lerp(BG,RED,k),width=max(2,int(4*U)))
    comps=["api-server","etcd","scheduler","controller"]; cw=CW/4
    for i,c in enumerate(comps):
        kk=ease((t-0.8-i*0.3)/0.4); f=M(24 if V else 28)
        d.text((X0+i*cw+(cw-d.textlength(c,font=f))/2,GY+cph/2-16*U),c,font=f,fill=lerp(PANEL,WHITE,kk))
    nodes=3; ny=GY+cph+90*U; gap=24*U; nw=(CW-gap*(nodes-1))/nodes; nh=GH*(0.62 if V else 0.5)
    for n in range(nodes):
        x=X0+n*(nw+gap); kk=ease((t-2-n*0.4)/0.5)
        if kk<=0: continue
        d.line([X0+CW/2,GY+cph,x+nw/2,ny],fill=lerp(BG,GREY,kk),width=max(2,int(3*U)))
        d.rounded_rectangle([x,ny,x+nw,ny+nh],int(16*U),fill=PANEL,outline=lerp(BG,BLUE,kk),width=max(2,int(3*U)))
        d.text((x+18*U,ny+14*U),f"node-{n+1}",font=B(28),fill=lerp(BG,WHITE,kk))
        cols=2 if V else 3; ps=(nw-36*U-(cols-1)*14*U)/cols; total=int(6*ease((t-3-n*0.3)/2))
        for p in range(total):
            px=x+18*U+(p%cols)*(ps+14*U); py=ny+60*U+(p//cols)*(ps+14*U)
            if py+ps<ny+nh-10*U: pod(d,px,py,ps,GREEN)

def s_hpa(d,t,L):
    title(d,t,"Автомасштабирование","HPA: поды растут вместе с трафиком")
    ch=GH*(0.42 if V else 0.6); cw=CW*(1 if V else 0.6)
    d.rounded_rectangle([X0,GY,X0+cw,GY+ch],int(16*U),fill=PANEL)
    d.text((X0+20*U,GY+14*U),"RPS",font=M(24),fill=GREY)
    N=60; shown=int(N*min(1,t/5)); pts=[]
    load=lambda i: 0.15+0.7*math.exp(-((i-30)/10)**2)+0.03*math.sin(i*1.3)
    for i in range(shown): pts.append((X0+20*U+i*(cw-40*U)/N,GY+ch-20*U-(ch-70*U)*load(i)))
    if len(pts)>1: d.line(pts,fill=BLUE,width=max(2,int(5*U)))
    cur=load(max(0,shown-1)); pods=max(2,round(2+18*(cur-0.15)/0.7))
    if V: px,py,pw=X0,GY+ch+40*U,CW
    else: px,py,pw=X0+CW*0.65,GY,CW*0.35
    d.text((px,py),f"{pods}",font=B(110),fill=GREEN); d.text((px+d.textlength(f"{pods}",font=B(110))+20*U,py+50*U),"подов",font=R(40),fill=GREY)
    cols=10; ps=(pw-(cols-1)*10*U)/cols
    for i in range(20):
        x=px+(i%cols)*(ps+10*U); y=py+160*U+(i//cols)*(ps+10*U)
        pod(d,x,y,ps,GREEN if i<pods else PANEL)
    d.text((px,py+160*U+2*(ps+10*U)+16*U),"kubectl get hpa → TARGET 70%",font=M(24),fill=GREY)

def s_heal(d,t,L):
    title(d,t,"Самовосстановление","Упавший под перезапускается сам")
    cols,rows=(4,3) if V else (6,2); gap=20*U; ps=min((CW-(cols-1)*gap)/cols,GH*0.42/rows*1.6)
    gw=cols*ps+(cols-1)*gap; gx=(W-gw)/2
    crash=[(5,1.2),(2,3.0),(9,4.6)]
    for i in range(cols*rows):
        x=gx+(i%cols)*(ps+gap); y=GY+(i//cols)*(ps+gap); col=GREEN; label=""
        for idx,tc in crash:
            if i==idx and tc<=t<tc+0.9: col=RED; label="CrashLoop"
            elif i==idx and tc+0.9<=t<tc+1.6: col=lerp(PANEL,GREEN,(t-tc-0.9)/0.7); label="Restarting"
        pod(d,x,y,ps,col)
        if label: d.text((x+ps/2-d.textlength(label,font=M(20))/2,y+ps+4*U),label,font=M(20),fill=WHITE)
    restarts=sum(1 for _,tc in crash if t>=tc+1.6)
    y=GY+rows*(ps+gap)+60*U
    stats=[(f"{restarts}","авто-рестартов"),("0","ручных действий"),("100%","доступность")]; sw=CW/3
    for i,(a,b) in enumerate(stats):
        x=X0+i*sw; d.text((x,y),a,font=B(56),fill=GREEN if i==2 else WHITE); d.text((x,y+74*U),b,font=R(28),fill=GREY)

def s_roll(d,t,L):
    title(d,t,"Обновления без простоя","Rolling update · GitOps · откат в один клик")
    th=GH*(0.26 if V else 0.32)
    d.rounded_rectangle([X0,GY,X0+CW,GY+th],int(16*U),fill=(6,8,12),outline=PANEL,width=max(2,int(3*U)))
    lines=["$ git push  →  ArgoCD: Synced ✓","$ helm upgrade app ./chart --set image.tag=v2","deployment \"app\" successfully rolled out"]
    chars=int(t*34); y=GY+22*U; f=M(22 if V else 28)
    for ln in lines:
        if chars<=0: break
        d.text((X0+24*U,y),ln[:chars],font=f,fill=GREEN if ln.startswith("deploy") else WHITE); chars-=len(ln)+8; y+=th/3.3
    n=8; gap=14*U; ps=(CW-(n-1)*gap)/n; py=GY+th+60*U; prog=ease((t-1.5)/4.5)*n
    for i in range(n):
        x=X0+i*(ps+gap); kk=max(0,min(1,prog-i))
        pod(d,x,py,ps,lerp(BLUE,GREEN,kk))
        lab="v2" if kk>0.5 else "v1"; d.text((x+ps/2-d.textlength(lab,font=B(26))/2,py+ps+8*U),lab,font=B(26),fill=GREEN if kk>0.5 else BLUE)
    y=py+ps+70*U; d.text((X0,y),"Доступность во время релиза",font=R(30),fill=WHITE)
    d.rounded_rectangle([X0,y+50*U,X0+CW,y+90*U],int(10*U),fill=GREEN)
    d.text((X0+CW-d.textlength("100%",font=B(30))-16*U,y+52*U),"100%",font=B(30),fill=BG)

def s_outro(d,t,L):
    cy=H*0.36; r=(170+20*math.sin(t*3))*U
    crosshair(d,W/2,cy,r,-t*0.6)
    k=ease((t-0.3)/0.6); ctext(d,cy+250*U,NAME,B(96 if V else 100),lerp(BG,WHITE,k))
    ctext(d,cy+370*U,"Kubernetes под контролем",R(40),lerp(BG,GREY,k))
    k2=ease((t-1.5)/0.6); f=B(70); w=d.textlength(SITE,font=f)+80*U; y=cy+460*U
    if k2>0:
        d.rounded_rectangle([(W-w)/2,y,(W+w)/2,y+110*U],int(55*U),fill=lerp(BG,RED,k2))
        ctext(d,y+16*U,SITE,f,lerp(RED,WHITE,k2))

SC=[s_intro,s_arch,s_hpa,s_heal,s_roll,s_outro]
def frame(t):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    off=(t*20*U)%(60*U)
    y=-60*U+off
    while y<H: d.line([(0,y),(W,y)],fill=GRID); y+=60*U
    i=max(j for j in range(6) if T[j]<=t); lt=t-T[i]; L=T[i+1]-T[i]
    SC[i](d,lt,L)
    # chrome
    d.text((X0,40*U),"◎ "+NAME,font=B(30),fill=RED)
    s=SITE; d.text((W-X0-d.textlength(s,font=M(28)),42*U),s,font=M(28),fill=GREY)
    d.rectangle([0,H-10*U,W*t/TOTAL,H],fill=RED)
    # fade between scenes
    fade=min(1,lt/0.25,(L-lt)/0.25) if i<5 else min(1,lt/0.25,(TOTAL-t)/0.6)
    if fade<1: im=Image.blend(Image.new("RGB",(W,H),BG),im,max(0,fade))
    return im
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-i","voice.mp3","-i","music.mp3","-filter_complex",
  f"[2:a]apad,volume=0.16,afade=t=in:d=1,afade=t=out:st={TOTAL-2}:d=2[m];[1:a]adelay=0|0,volume=1.0[v];[v][m]amix=inputs=2:duration=longest:normalize=0[a]",
  "-map","0:v","-map","[a]","-t",f"{TOTAL}","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",OUT],stdin=subprocess.PIPE)
for n in range(int(TOTAL*FPS)): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
