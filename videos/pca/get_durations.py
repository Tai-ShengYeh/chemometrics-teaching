import sys, subprocess, json
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
NARR = Path(__file__).resolve().parent / "assets" / "narration"
SUBTITLES = [
    "一條光譜上百個數字，PCA 幫我們讀懂",
    "每個樣本是 100 維空間的一點，看不出來",
    "SNV 校正散射，凸顯真正的化學差異",
    "PC1＝最大分散方向，PC2 與它垂直",
    "X ≈ T·Pᵀ：分數看樣本，負荷量看波長",
    "前 3 個主成分捕捉 99% 的變異",
    "PCA 沒看過脂肪，樣本卻依脂肪自動排列",
    "落在 95% 橢圓外 = 可疑樣本，要檢查",
    "930 nm 起伏 = 脂肪 C–H 吸收帶",
    "PCA 非監督：探索分群找異常，不做預測",
    "光譜 → 前處理 → PCA → 分數 / 負荷量 / 陡坡",
    "PCA：把上百個波長，壓縮成看得懂的方向",
    "下一支：PLS 回歸，從光譜預測含量",
]
N = len(SUBTITLES)
def dur(p):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",str(p)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return float(json.loads(r.stdout.decode('utf-8'))["format"]["duration"])
def main():
    PAGES_JS, timings, total = [], [], 0
    for i in range(1, N+1):
        p = NARR / f"page-{i:02d}.mp3"
        if not p.exists(): print(f"missing {p.name}"); return
        d = dur(p); pd = int(round(d + 3.0)); total += pd; timings.append(pd)
        PAGES_JS.append(f'  {{ i: {i}, dur: {pd}, sub: "{SUBTITLES[i-1]}" }}')
        print(f"page-{i:02d}: {d:.2f}s -> {pd}s")
    print("\nconst PAGES = [\n" + ",\n".join(PAGES_JS) + "\n];")
    print("\nPAGES_TIMINGS = [" + ", ".join(f'{{"i": {i+1}, "dur": {d}}}' for i,d in enumerate(timings)) + "]")
    print(f"\nTOTAL = {total}s | record ms = {total*1000+800}")
if __name__ == "__main__": main()
