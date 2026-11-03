import re, numpy as np, subprocess, sys
sys.argv=['x','info']
import v5
SR=48000; N=int(v5.TOTAL*SR)+SR
out=np.zeros(N)
rng=np.random.default_rng(1)
def whoosh(d=0.35):
    n=int(d*SR); x=rng.standard_normal(n); t=np.linspace(0,1,n)
    env=np.sin(np.pi*t)**2
    # filtro passa-banda simples variando
    y=np.convolve(x,np.ones(12)/12,'same')-np.convolve(x,np.ones(80)/80,'same')
    return y*env*0.10
def tick():
    n=int(0.06*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*1800*t)*np.exp(-t*70)*0.12
def thud():
    n=int(0.25*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*90*t*(1-t*1.5))*np.exp(-t*16))*0.35
def add(T,s):
    i=int(T*SR); out[i:i+len(s)]+=s[:max(0,N-i)]
src=open('v5.py').read()
ev=[]
for sc in v5.SC[1:]: ev.append((sc[0],'w'))
ev.append((v5.BSTART,'w'))
for m in re.finditer(r'(?:strike|check|bullet)\(c, [^)]*?, t, ([\d.]+)',src): ev.append((float(m.group(1)),'t'))
for m in re.finditer(r'ap\(t, ([\d.]+)(?:, \.3)?\), pop=True',src): ev.append((float(m.group(1)),'h'))
for S,k in ev:
    T=v5.fwd(S)
    if k=='w': add(max(0,T-0.12),whoosh())
    elif k=='t': add(T,tick())
    else: add(T,thud())
add(0.05,whoosh(0.5))
import wave
w=wave.open('sfx.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes()); w.close()
print(len(ev))
