# Render pipeline — Tecator PCA video -> renders/nir_pca.mp4
import os, sys, shutil, subprocess, glob
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
ROOT = Path(__file__).resolve().parent
RENDERS = ROOT/"renders"; RENDERS.mkdir(parents=True, exist_ok=True)
NARR = ROOT/"assets"/"narration"; REC = ROOT/"record.cjs"; FINAL = RENDERS/"nir_pca.mp4"
PAGES_TIMINGS = [{"i":1,"dur":19},{"i":2,"dur":24},{"i":3,"dur":22},{"i":4,"dur":23},{"i":5,"dur":22},{"i":6,"dur":25},{"i":7,"dur":26},{"i":8,"dur":19},{"i":9,"dur":21},{"i":10,"dur":17},{"i":11,"dur":22},{"i":12,"dur":10},{"i":13,"dur":10}]
def node_env():
    e=os.environ.copy(); e["NODE_PATH"]=os.path.join(e.get("TEMP","C:\\Temp"),"cvs-render","node_modules"); return e
def audio():
    print("[1/3] master audio"); m=RENDERS/"master_audio.mp3"
    if m.exists(): os.remove(m)
    pad=[]
    for p in PAGES_TIMINGS:
        s=NARR/f"page-{p['i']:02d}.mp3"; d=RENDERS/f"pad-{p['i']:02d}.mp3"
        if not s.exists(): raise FileNotFoundError(s)
        if d.exists(): os.remove(d)
        r=subprocess.run(["ffmpeg","-y","-i",str(s),"-af","apad","-t",str(p['dur']),str(d)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if r.returncode: print(r.stderr.decode('utf-8','ignore')); r.check_returncode()
        pad.append(d)
    cc=RENDERS/"cc.txt"
    with open(cc,"w",encoding="utf-8") as f:
        for p in pad: f.write(f"file '{p.name}'\n")
    r=subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(cc),"-c","copy",str(m)],cwd=str(RENDERS),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode: print(r.stderr.decode('utf-8','ignore')); r.check_returncode()
    for p in pad:
        try: os.remove(p)
        except: pass
    try: os.remove(cc)
    except: pass
    print("  ok", m)
def rec():
    print("[2/3] record (~261s)")
    for f in glob.glob(str(RENDERS/"*.webm")):
        try: os.remove(f)
        except: pass
    subprocess.run(["node",str(REC)],cwd=str(ROOT),env=node_env(),check=True,shell=True)
    w=glob.glob(str(RENDERS/"*.webm"))
    if not w: raise FileNotFoundError("no webm")
    t=RENDERS/"video.webm"
    if t.exists(): os.remove(t)
    shutil.move(w[0],t); print("  ok",t)
def mux():
    print("[3/3] mux")
    if FINAL.exists(): os.remove(FINAL)
    r=subprocess.run(["ffmpeg","-y","-i",str(RENDERS/"video.webm"),"-i",str(RENDERS/"master_audio.mp3"),"-map","0:v","-map","1:a","-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","192k","-shortest",str(FINAL)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode: print(r.stderr.decode('utf-8','ignore')); r.check_returncode()
    print("  ok",FINAL)
try:
    print("=== Tecator PCA render ==="); audio(); rec(); mux(); print(f"=== DONE: {FINAL} ===")
except Exception as e:
    print("[ERROR]",e); sys.exit(1)
