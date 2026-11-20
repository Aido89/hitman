"""Hitman DevOps promo (KK): animated infographic video. Usage: python3 make.py W H out.mp4"""
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

def s_intro(d,t,L):
    cy=H*0.40; r=150*U*ease(t/0.8)
    crosshair(d,W/2,cy,r,t*0.8)
    n=int(len(NAME)*min(1,max(0,(t-0.6)/1.0))); ctext(d,cy+230*U,NAME[:n]+("▌" if int(t*3)%2 else " "),B(96 if V else 100),WHITE)
    k=ease((t-1.8)/0.6); ctext(d,cy+360*U,"Сіз үшін жұмыс істейтін DevOps",R(40),lerp(BG,GREY,k))
    tags=["CI/CD","Kubernetes","Monitoring","IaC"]; f=M(30); gap=24*U
    ws=[d.textlength(s,font=f)+40*U for s in tags]
    rows=[tags[:2],tags[2:]] if V else [tags]; y=cy+450*U; i=0
    for row in rows:
        tw=sum(ws[i:i+len(row)])+gap*(len(row)-1); x=(W-tw)/2
        for s in row:
            kk=ease((t-2.4-i*0.25)/0.4)
            if kk>0:
                d.rounded_rectangle([x,y,x+ws[i],y+56*U],int(28*U),outline=lerp(BG,RED,kk),width=max(2,int(3*U)))
                d.text((x+20*U,y+10*U),s,font=f,fill=lerp(BG,WHITE,kk))
            x+=ws[i]+gap; i+=1
        y+=80*U

def s_cicd(d,t,L):
    title(d,t,"CI/CD конвейері","Жинау · тест · деплой — минуттарда")
    st=["commit","build","test","deploy"]; n=len(st)
    if V:  # vertical pipeline
        bh=GH*0.13; bx=X0+CW*0.1; bw=CW*0.8
        for i,s in enumerate(st):
            y=GY+i*bh*1.45; k=ease((t-0.6-i*0.9)/0.6)
            col=lerp(PANEL,GREEN if i<3 else RED,k)
            d.rounded_rectangle([bx,y,bx+bw,y+bh],int(16*U),fill=PANEL,outline=col,width=max(2,int(4*U)))
            d.rounded_rectangle([bx,y+bh-8*U,bx+bw*k,y+bh],int(4*U),fill=col)
            d.text((bx+30*U,y+bh/2-22*U),s.upper(),font=B(40),fill=WHITE)
            d.text((bx+bw-90*U,y+bh/2-26*U),"✓" if k>=1 else "…",font=B(48),fill=col)
            if i<n-1: d.line([W/2,y+bh,W/2,y+bh*1.45],fill=GREY,width=max(2,int(3*U)))
        cy=GY+n*bh*1.45+20*U
    else:
        bw=CW/n*0.78; bh=GH*0.25
        for i,s in enumerate(st):
            x=X0+i*CW/n; k=ease((t-0.6-i*0.9)/0.6); col=lerp(PANEL,GREEN if i<3 else RED,k)
            d.rounded_rectangle([x,GY,x+bw,GY+bh],int(16*U),fill=PANEL,outline=col,width=max(2,int(4*U)))
            d.rounded_rectangle([x,GY+bh-10*U,x+bw*k,GY+bh],int(4*U),fill=col)
            ctext(d,GY+bh*0.22,s.upper(),B(38),WHITE,x+(bw-d.textlength(s.upper(),font=B(38)))/2)
            ctext(d,GY+bh*0.55,"✓" if k>=1 else "…",B(44),col,x+bw/2-14*U)
            if i<n-1:
                ax=x+bw; d.line([ax+8*U,GY+bh/2,x+CW/n-8*U,GY+bh/2],fill=GREY,width=max(2,int(3*U)))
        cy=GY+bh+60*U
    # bar comparison
    k=ease((t-4.2)/1.2); lw=CW*0.30; mx=CW-lw-140*U
    for j,(lab,val,col,txt) in enumerate([("Қолмен",1.0,GREY,"4 сағ"),("Hitman DevOps",0.06,GREEN,"4 мин")]):
        y=cy+j*70*U; d.text((X0,y),lab,font=R(32),fill=WHITE)
        d.rounded_rectangle([X0+lw,y,X0+lw+max(8*U,mx*val*k),y+44*U],int(8*U),fill=col)
        d.text((X0+lw+mx*val*k+14*U,y+4*U),txt,font=B(32),fill=col)

def s_k8s(d,t,L):
    title(d,t,"Docker + Kubernetes","Кез келген жүктемеге масштабтау")
    cols,rows=(6,4) if V else (10,3); gw=CW*(1 if V else 0.62); cell=gw/cols
    gh=cell*rows; reps=int(1+(cols*rows-1)*ease((t-0.8)/3.5))
    for i in range(cols*rows):
        x=X0+(i%cols)*cell; y=GY+(i//cols)*cell; on=i<reps
        d.rounded_rectangle([x+6*U,y+6*U,x+cell-6*U,y+cell-6*U],int(12*U),fill=BLUE if on else PANEL)
        if on: d.text((x+cell/2-14*U,y+cell/2-22*U),"⬢",font=R(36),fill=WHITE)
    d.text((X0,GY+gh+20*U),f"kubectl scale --replicas={reps}",font=M(30),fill=GREEN)
    # gauge
    if V: gx,gy,gr=W/2,GY+gh+260*U,150*U
    else: gx,gy,gr=X0+CW*0.84,GY+gh*0.55,160*U
    load=95-60*ease((t-0.8)/3.5); wd=int(28*U)
    d.arc([gx-gr,gy-gr,gx+gr,gy+gr],150,390,fill=PANEL,width=wd)
    col=lerp(GREEN,RED,(load-35)/60); d.arc([gx-gr,gy-gr,gx+gr,gy+gr],150,150+240*load/100,fill=col,width=wd)
    s=f"{int(load)}%"; ctext(d,gy-40*U,s,B(64),WHITE,gx-d.textlength(s,font=B(64))/2)
    ctext(d,gy+40*U,"CPU",R(30),GREY,gx-d.textlength("CPU",font=R(30))/2)

def s_mon(d,t,L):
    title(d,t,"Мониторинг 24/7","Мәселені пайдаланушылардан бұрын білеміз")
    cw=CW; ch=GH*(0.45 if V else 0.6)
    d.rounded_rectangle([X0,GY,X0+cw,GY+ch],int(16*U),fill=PANEL)
    for g in range(1,4): d.line([X0,GY+ch*g/4,X0+cw,GY+ch*g/4],fill=GRID,width=1)
    N=80; shown=int(N*min(1,t/3.5)); pts=[]
    for i in range(shown):
        v=0.35+0.08*math.sin(i*0.7)+0.05*math.sin(i*1.9)
        if 48<i<56: v+=0.4*math.sin((i-48)/8*math.pi)
        if i>=56: v=0.3+0.04*math.sin(i)
        pts.append((X0+20*U+i*(cw-40*U)/N,GY+ch-ch*v))
    if len(pts)>1: d.line(pts,fill=GREEN,width=max(2,int(4*U)))
    d.line([X0,GY+ch*0.35,X0+cw,GY+ch*0.35],fill=RED,width=max(1,int(2*U)))
    d.text((X0+16*U,GY+ch*0.35-40*U),"SLO p99 300ms",font=M(24),fill=RED)
    if shown>50:
        x,y=pts[min(52,len(pts)-1)]; r=(10+8*abs(math.sin(t*6)))*U
        d.ellipse([x-r,y-r,x+r,y+r],outline=RED,width=max(2,int(3*U)))
        d.rounded_rectangle([x-150*U,GY+12*U,x+150*U,GY+62*U],int(10*U),fill=RED)
        d.text((x-135*U,GY+20*U),"⚠ ALERT → on-call",font=B(26),fill=WHITE)
    stats=[("99.9%","аптайм"),("< 1 мин","әрекет"),("24/7","кезекшілік")]
    k=ease((t-2)/1.0); y=GY+ch+40*U; n=3; sw=cw/n
    for i,(a,b) in enumerate(stats):
        x=X0+i*sw; kk=ease((t-2-i*0.3)/0.6)
        d.text((x,y),a,font=B(54 if not V else 48),fill=lerp(BG,GREEN if i==0 else WHITE,kk))
        d.text((x,y+75*U),b,font=R(30),fill=lerp(BG,GREY,kk))

def s_iac(d,t,L):
    title(d,t,"Infrastructure as Code","Ашық · қайталанатын · бақылауда")
    lines=["$ terraform plan","  + aws_vpc.main","  + aws_eks_cluster.prod","  + aws_rds_instance.db","$ terraform apply -auto-approve","Apply complete! 12 added, 0 destroyed."]
    th=GH*(0.5 if V else 0.62); tw=CW*(1 if V else 0.6)
    d.rounded_rectangle([X0,GY,X0+tw,GY+th],int(16*U),fill=(6,8,12),outline=PANEL,width=max(2,int(3*U)))
    for i,c in enumerate([(255,95,86),(255,189,46),(39,201,63)]): d.ellipse([X0+24*U+i*36*U,GY+20*U,X0+48*U+i*36*U,GY+44*U],fill=c)
    chars=int(t*28); y=GY+70*U; f=M(26 if V else 28)
    for ln in lines:
        if chars<=0: break
        s=ln[:chars]; chars-=len(ln)+6
        d.text((X0+28*U,y),s,font=f,fill=GREEN if ln.startswith("Apply") else (WHITE if ln.startswith("$") else BLUE)); y+=th/8
    # donut
    if V: cx,cy,r=W/2,GY+th+230*U,150*U
    else: cx,cy,r=X0+CW*0.83,GY+th/2,170*U
    k=ease((t-1)/2.5); wd=int(34*U)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=PANEL,width=wd)
    d.arc([cx-r,cy-r,cx+r,cy+r],-90,-90+360*k,fill=RED,width=wd)
    s=f"{int(100*k)}%"; d.text((cx-d.textlength(s,font=B(60))/2,cy-45*U),s,font=B(60),fill=WHITE)
    s="git-те"; d.text((cx-d.textlength(s,font=R(30))/2,cy+30*U),s,font=R(30),fill=GREY)

def s_outro(d,t,L):
    cy=H*0.36; r=(170+20*math.sin(t*3))*U
    crosshair(d,W/2,cy,r,-t*0.6)
    k=ease((t-0.3)/0.6); ctext(d,cy+250*U,NAME,B(96 if V else 100),lerp(BG,WHITE,k))
    ctext(d,cy+370*U,"Код продакшнға — дәл нысанаға",R(36 if V else 40),lerp(BG,GREY,k))
    k2=ease((t-1.5)/0.6); f=B(70); w=d.textlength(SITE,font=f)+80*U; y=cy+460*U
    if k2>0:
        d.rounded_rectangle([(W-w)/2,y,(W+w)/2,y+110*U],int(55*U),fill=lerp(BG,RED,k2))
        ctext(d,y+16*U,SITE,f,lerp(RED,WHITE,k2))

SC=[s_intro,s_cicd,s_k8s,s_mon,s_iac,s_outro]
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
