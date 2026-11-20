"""Hitman DevOps — Linux promo: animated infographic video. Usage: python3 make.py W H out.mp4"""
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
    cy=H*0.38; k=ease(t/0.6)
    # terminal prompt icon
    bw,bh=300*U,200*U; d.rounded_rectangle([W/2-bw/2,cy-bh/2,W/2+bw/2,cy+bh/2],int(24*U),outline=lerp(BG,RED,k),width=max(3,int(6*U)),fill=PANEL)
    d.text((W/2-bw/2+40*U,cy-60*U),">_" if int(t*3)%2 else ">",font=B(110),fill=lerp(BG,GREEN,k))
    n=int(len(NAME)*min(1,max(0,(t-0.5)/1.0))); ctext(d,cy+170*U,NAME[:n],B(96 if V else 100),WHITE)
    k2=ease((t-1.6)/0.6); ctext(d,cy+290*U,"Linux-серверлер бақылауда",R(40),lerp(BG,GREY,k2))
    tags=["Ubuntu","Debian","RHEL","Rocky"]; f=M(30); gap=24*U
    ws=[d.textlength(s,font=f)+40*U for s in tags]
    rows=[tags[:2],tags[2:]] if V else [tags]; y=cy+380*U; i=0
    for row in rows:
        tw=sum(ws[i:i+len(row)])+gap*(len(row)-1); x=(W-tw)/2
        for s in row:
            kk=ease((t-2.2-i*0.25)/0.4)
            if kk>0:
                d.rounded_rectangle([x,y,x+ws[i],y+56*U],int(28*U),outline=lerp(BG,RED,kk),width=max(2,int(3*U)))
                d.text((x+20*U,y+10*U),s,font=f,fill=lerp(BG,WHITE,kk))
            x+=ws[i]+gap; i+=1
        y+=80*U

def s_harden(d,t,L):
    title(d,t,"Серверлерді қорғау","Чек-лист бойынша нөлден hardening")
    items=[("SSH тек кілтпен","PasswordAuthentication no"),("Файрвол","ufw default deny incoming"),("fail2ban","bantime = 1h, maxretry = 3"),("Автожаңартулар","unattended-upgrades")]
    lw=CW*(1 if V else 0.62); ih=GH*(0.15 if V else 0.2)
    for i,(a,b) in enumerate(items):
        y=GY+i*ih*1.18; k=ease((t-0.6-i*1.4)/0.5)
        col=lerp(PANEL,GREEN,k)
        d.rounded_rectangle([X0,y,X0+lw,y+ih],int(14*U),fill=PANEL,outline=col,width=max(2,int(3*U)))
        bx=X0+20*U; bs=ih*0.5; by=y+(ih-bs)/2
        d.rounded_rectangle([bx,by,bx+bs,by+bs],int(8*U),outline=col,width=max(2,int(3*U)),fill=col if k>=1 else PANEL)
        if k>=1: d.text((bx+bs*0.18,by-bs*0.05),"✓",font=B(int(bs/U*0.8)),fill=BG)
        d.text((bx+bs+24*U,y+ih*0.14),a,font=B(32 if V else 34),fill=WHITE)
        d.text((bx+bs+24*U,y+ih*0.56),b,font=M(24),fill=GREY)
    # attack counter
    if V: cx,cy=W/2,GY+4*ih*1.18+190*U
    else: cx,cy=X0+CW*0.84,GY+GH*0.4
    blocked=int(1847*ease((t-3)/4)); r=150*U; k=ease((t-2.5)/0.6)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=lerp(BG,RED,k),width=max(3,int(8*U)))
    s=f"{blocked}"; d.text((cx-d.textlength(s,font=B(66))/2,cy-55*U),s,font=B(66),fill=lerp(BG,WHITE,k))
    s="бұғатталды"; d.text((cx-d.textlength(s,font=R(28))/2,cy+25*U),s,font=R(28),fill=lerp(BG,GREY,k))

def s_perf(d,t,L):
    title(d,t,"Өнімділік","CPU · RAM · дискілер жүктемесіз")
    th=GH*(0.55 if V else 0.75); tw=CW*(1 if V else 0.62)
    d.rounded_rectangle([X0,GY,X0+tw,GY+th],int(16*U),fill=(6,8,12),outline=PANEL,width=max(2,int(3*U)))
    d.text((X0+24*U,GY+16*U),"$ htop",font=M(26),fill=GREEN)
    cores=8; rh=(th-150*U)/cores; calm=ease((t-2.5)/2)
    for c in range(cores):
        y=GY+70*U+c*rh; v=0.9-0.55*calm+0.08*math.sin(t*5+c*1.3)
        v=max(0.05,min(1,v)); bw=tw-160*U
        d.text((X0+24*U,y),f"{c}",font=M(24),fill=GREY)
        d.rectangle([X0+70*U,y+4*U,X0+70*U+bw,y+rh-10*U],fill=PANEL)
        d.rectangle([X0+70*U,y+4*U,X0+70*U+bw*v,y+rh-10*U],fill=lerp(GREEN,RED,(v-0.4)/0.5))
    mem=0.92-0.5*calm; y=GY+th-60*U
    d.text((X0+24*U,y),"Mem",font=M(24),fill=GREY); bw=tw-160*U
    d.rectangle([X0+90*U,y+4*U,X0+90*U+bw,y+30*U],fill=PANEL); d.rectangle([X0+90*U,y+4*U,X0+90*U+bw*mem,y+30*U],fill=BLUE)
    # load average stats
    stats=[(f"{4.8-3.6*calm:.1f}","load avg"),(f"{int(92-50*calm)}%","RAM"),(f"{int(15+75*calm)} ms→" if False else f"{int(800-680*calm)} ms","жауап")]
    if V: sx,sy,sw,sh=X0,GY+th+40*U,CW/3,0
    else: sx,sy,sw,sh=X0+CW*0.68,GY+20*U,0,th/3
    for i,(a,b) in enumerate(stats):
        x=sx+i*sw; y=sy+i*sh
        d.text((x,y),a,font=B(52),fill=GREEN if calm>0.9 else WHITE); d.text((x,y+68*U),b,font=R(28),fill=GREY)

def s_auto(d,t,L):
    title(d,t,"Автоматтандыру","Bash + Ansible: бір команда — барлық сервер")
    th=GH*(0.3 if V else 0.38); 
    d.rounded_rectangle([X0,GY,X0+CW,GY+th],int(16*U),fill=(6,8,12),outline=PANEL,width=max(2,int(3*U)))
    lines=["$ ansible-playbook site.yml -i prod","PLAY [all] ********************","ok=48  changed=12  failed=0"]
    chars=int(t*32); y=GY+24*U; f=M(24 if V else 28)
    for ln in lines:
        if chars<=0: break
        d.text((X0+24*U,y),ln[:chars],font=f,fill=GREEN if ln.startswith("ok") else WHITE); chars-=len(ln)+8; y+=th/3.4
    cols,rows=(6,5) if V else (12,3); n=cols*rows; cell=CW/cols; gy=GY+th+40*U
    done=int(n*ease((t-1.5)/4))
    for i in range(n):
        x=X0+(i%cols)*cell; y=gy+(i//cols)*cell*0.8; ch=cell*0.8
        col=GREEN if i<done else (lerp(PANEL,BLUE,0.5+0.5*math.sin(t*8)) if i==done else PANEL)
        d.rounded_rectangle([x+6*U,y+6*U,x+cell-6*U,y+ch-6*U],int(10*U),fill=col)
        for j in range(3): d.line([x+18*U,y+ch*(0.3+j*0.2),x+cell-18*U,y+ch*(0.3+j*0.2)],fill=BG,width=max(1,int(3*U)))
    s=f"{done}/{n} сервер"; d.text((X0,gy+rows*cell*0.8+16*U),s,font=B(34),fill=GREEN)

def s_backup(d,t,L):
    title(d,t,"Күн сайын бэкап","Тексерілген қалпына келтіру")
    days=["Дс","Сс","Ср","Бс","Жм","Сб","Жс"]; n=7; bw=CW/n; bh=GH*(0.3 if V else 0.45)
    for i,dd in enumerate(days):
        k=ease((t-0.5-i*0.35)/0.5); x=X0+i*bw; h=bh*(0.55+0.35*((i*37)%10)/10)*k
        d.rounded_rectangle([x+10*U,GY+bh-h,x+bw-10*U,GY+bh],int(8*U),fill=BLUE)
        if k>=1: d.text((x+bw/2-14*U,GY+bh-h-50*U),"✓",font=B(36),fill=GREEN)
        d.text((x+bw/2-d.textlength(dd,font=R(28))/2,GY+bh+12*U),dd,font=R(28),fill=GREY)
    y=GY+bh+80*U
    d.text((X0,y),"$ restic restore latest --target /srv",font=M(26 if V else 28),fill=WHITE)
    k=ease((t-3)/2); pw=CW; d.rounded_rectangle([X0,y+50*U,X0+pw,y+90*U],int(10*U),fill=PANEL)
    d.rounded_rectangle([X0,y+50*U,X0+max(10*U,pw*k),y+90*U],int(10*U),fill=GREEN)
    d.text((X0,y+110*U),f"қалпына келтірілді {int(k*100)}%"+("  ·  RPO 24 сағ  ·  RTO < 15 мин" if k>=1 else ""),font=B(30 if V else 32),fill=GREEN if k>=1 else WHITE)

def s_outro(d,t,L):
    cy=H*0.36; r=(170+20*math.sin(t*3))*U
    crosshair(d,W/2,cy,r,-t*0.6)
    k=ease((t-0.3)/0.6); ctext(d,cy+250*U,NAME,B(96 if V else 100),lerp(BG,WHITE,k))
    ctext(d,cy+370*U,"Жай ғана жұмыс істейтін Linux",R(40),lerp(BG,GREY,k))
    k2=ease((t-1.5)/0.6); f=B(70); w=d.textlength(SITE,font=f)+80*U; y=cy+460*U
    if k2>0:
        d.rounded_rectangle([(W-w)/2,y,(W+w)/2,y+110*U],int(55*U),fill=lerp(BG,RED,k2))
        ctext(d,y+16*U,SITE,f,lerp(RED,WHITE,k2))

SC=[s_intro,s_harden,s_perf,s_auto,s_backup,s_outro]
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
