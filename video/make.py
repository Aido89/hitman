from PIL import Image, ImageDraw, ImageFont
import subprocess, textwrap
F="/usr/share/fonts/truetype/dejavu/"
big=ImageFont.truetype(F+"DejaVuSans-Bold.ttf",76); mid=ImageFont.truetype(F+"DejaVuSans.ttf",40); mono=ImageFont.truetype(F+"DejaVuSansMono.ttf",30)
slides=[("HITMAN IT","DevOps, который работает на вас","$ ./deploy --target=prod"),
("CI/CD","Сборка · тесты · деплой — за минуты","git push → build ✓ → test ✓ → deploy ✓"),
("Docker + Kubernetes","Стабильность и масштабирование","kubectl scale deploy/app --replicas=10"),
("Мониторинг 24/7","Узнаём о проблеме раньше пользователей","alert: latency p99 > 300ms → on-call"),
("Infrastructure as Code","Прозрачно · воспроизводимо · под контролем","terraform apply  # 12 added, 0 destroyed"),
("HITMAN IT","Код в продакшн — точно в цель","◎  hitman-it")]
lines=[l for l in open("script.txt").read().splitlines() if l.strip()]
total=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","voice.mp3"]))+1.0
w=[len(l) for l in lines]; durs=[total*x/sum(w) for x in w]
lst=open("list.txt","w")
for i,(t,s,c) in enumerate(slides):
    im=Image.new("RGB",(1920,1080),(12,16,24)); d=ImageDraw.Draw(im)
    for y in range(0,1080,60): d.line([(0,y),(1920,y)],fill=(20,28,40))
    d.rectangle([120,300,132,700],fill=(230,40,60))
    d.text((180,320),t,font=big,fill=(255,255,255))
    d.text((180,440),s,font=mid,fill=(170,190,210))
    d.rounded_rectangle([180,560,1700,640],12,fill=(24,32,46))
    d.text((210,580),c,font=mono,fill=(80,220,140))
    d.text((1700,1000),f"{i+1}/6",font=mono,fill=(90,100,120))
    im.save(f"s{i}.png"); lst.write(f"file 's{i}.png'\nduration {durs[i]:.3f}\n")
lst.write("file 's5.png'\n"); lst.close()
