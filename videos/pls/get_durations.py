import sys, subprocess, json
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
NARR = Path(__file__).resolve().parent / "assets" / "narration"
SUBTITLES = [
    "PLS：把光譜變成可預測的脂肪數字",
    "目標：用光譜 X 預測脂肪 y，又快又不破壞",
    "校正：用「光譜＋真值」訓練出預測模型",
    "PLS 找「同時解釋光譜又預測脂肪」的方向",
    "潛在變量：最大化 X 與 y 的共變異",
    "180 訓練 / 60 測試，留一份驗證真實表現",
    "交叉驗證選在轉折點：4 個潛在變量",
    "測試集 R²=0.96，點緊貼 1:1 對角線",
    "RMSEP≈2.8%、RPD=5.2（>3 堪用，>5 優秀）",
    "係數尖峰在 928 nm = 脂肪 C–H 訊號",
    "可上線即時品管，但超出範圍要重新驗證",
    "探索用 PCA，預測用 PLS，獨立測試驗證",
    "PLS：把幾秒的掃描，變成可信的數字",
    "下一步：用 Orange 不寫程式重現整套流程",
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
