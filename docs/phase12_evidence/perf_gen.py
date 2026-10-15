import json
D1={"NoFx":(4.7,4.9),"Animator":(9.6,7.7),"Motion":(13.3,13.0),"MotionRig":(7.6,7.5),"Shape":(13.5,9.3),"Cursor":(12.1,8.8),"Connector":(10.7,10.6),"Look":(7.4,8.0),"Relief":(5.3,5.0),"Reflection":(12.1,8.5),"PageCurl":(10.7,7.5),"Bloom":(5.5,4.9),"LongShadow":(5.4,5.2),
"UIBlock":(22.5,15.6),"ProgressRing":(27.6,19.8),"ProgressBar":(27.9,20.2),"TextLetter":(20.0,19.4),"TextWord":(20.7,19.3),"TextLine":(19.9,19.5),"Callout":(29.1,14.9),"CardStack":(89.1,28.4),"StatCard":(26.0,16.9),"ClickDemo":(28.0,17.1)}
D4={"NoFx":(18.4,18.4),"Animator":(18.6,18.6),"Motion":(36.6,33.9),"MotionRig":(18.8,18.4),"Shape":(25.5,18.2),"Cursor":(29.8,24.7),"Connector":(25.2,18.6),"Look":(30.5,25.7),"Relief":(18.6,18.1),"Reflection":(26.2,22.4),"PageCurl":(23.8,20.5),"Bloom":(19.4,19.0),"LongShadow":(18.7,19.1),
"UIBlock":(40.7,31.9),"ProgressRing":(46.6,38.5),"ProgressBar":(47.3,38.2),"TextLetter":(36.6,35.1),"TextWord":(51.2,37.1),"TextLine":(36.3,39.0),"Callout":(84.0,85.6),"CardStack":(121.1,65.9),"StatCard":(59.0,33.0),"ClickDemo":(105.7,88.9)}
rows=[]
for k in D1:
    if k=="NoFx": continue
    a1,b1=D1[k]; a4,b4=D4[k]
    d1a,d1b=round(a1-D1["NoFx"][0],1),round(b1-D1["NoFx"][1],1)
    d4a,d4b=round(a4-D4["NoFx"][0],1),round(b4-D4["NoFx"][1],1)
    flag="**>5**" if max(d1a,d1b)>5 else ("(>5 first run only)" if d1a>5 else "")
    flag=("**>5 ms**" if d1b>5 else ("first run only" if d1a>5 else "ok"))
    rows.append((k,a1,b1,d1a,d1b,a4,b4,d4a,d4b,flag))
out=["| Product | 1080p first | 1080p second | Δ first | **Δ second** | 4K first | 4K second | Δ first | Δ second | >5 ms at 1080p? |","|---|---|---|---|---|---|---|---|---|---|"]
for r in rows: out.append("| "+" | ".join(str(x) for x in r)+" |")
open("perf_table.md","w",encoding="utf-8").write("\n".join(out)); print("\n".join(out))
