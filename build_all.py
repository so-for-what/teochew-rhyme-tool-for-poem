#!/usr/bin/env python3
"""
一键构建脚本：从原始数据到最终交付
========================================
用法：
  python3 build_all.py

会依次执行：
  1. 检查所需原始数据是否存在，提示下载链接
  2. 生成 data/rhyme_by_rhyme_*.csv（古韵→潮汕音韵母对照表）
  3. 生成 output/data.js + output/index.html（交互页面）
  4. 生成 output/rhyme_tool_standalone.html（独立单文件版）

依赖：Python 3.8+，无需额外安装包（只使用标准库）。
"""

import json, csv, os, re, sys
from collections import defaultdict

# ── 路径配置（相对于本脚本所在目录）──
BASE = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(BASE, 'raw')
DATA = os.path.join(BASE, 'data')
CODE = os.path.join(BASE, 'code')
OUT  = os.path.join(BASE, 'output')
os.makedirs(RAW, exist_ok=True)
os.makedirs(DATA, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

print("=" * 60)
print("潮汕音填词押韵查询工具 — 一键构建")
print("=" * 60)

# ═════════════════════════════════════════════
# 步骤 0：检查原始数据
# ═════════════════════════════════════════════

def check_raw(filepath, name, url):
    """检查原始数据文件是否存在，不存在时给出提示"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✅ {name}: {size//1024}KB")
        return True
    else:
        print(f"  ⚠️ {name}: 未找到")
        print(f"     请下载: {url}")
        print(f"     保存到: {filepath}")
        return False

print("\n[0/4] 检查原始数据...\n")

PINGS_HUI_URL = "https://cdn.jsdelivr.net/gh/charlesix59/chinese_word_rhyme@main/data/Pingshui_Rhyme.json"
CILIN_URL     = "https://cdn.jsdelivr.net/gh/charlesix59/chinese_word_rhyme@main/data/Cilin_Rhyme.json"
TEOCHEW_URL   = "https://cdn.jsdelivr.net/gh/hokkien-writing/teochew-lexicon@main/character.csv"
DIEZIU_URL    = "https://raw.githubusercontent.com/kahaani/dieghv/master/dieziu.dict.yaml"
GEKION_URL    = "https://raw.githubusercontent.com/kahaani/dieghv/master/gekion.dict.yaml"
ENTRIES_URL   = "https://github.com/hokkien-writing/dataset/tree/master/external/dieghv"

all_ok = True
all_ok &= check_raw(os.path.join(RAW, 'Pingshui_Rhyme.json'), '平水韵', PINGS_HUI_URL)
all_ok &= check_raw(os.path.join(RAW, 'Cilin_Rhyme.json'), '词林正韵', CILIN_URL)
all_ok &= check_raw(os.path.join(RAW, 'character.csv'), '潮汕音 P0', TEOCHEW_URL)
all_ok &= check_raw(os.path.join(RAW, 'dieziu.dict.yaml'), '潮州音字典', DIEZIU_URL)
all_ok &= check_raw(os.path.join(RAW, 'gekion.dict.yaml'), '揭阳音字典', GEKION_URL)

# entries.yml 从 DATA 目录的预解析json加载
entries_path = os.path.join(RAW, 'entries_parsed.json')
if not os.path.exists(entries_path):
    # 检查是否有已经解析好的版本
    fallback = os.path.join(DATA, '..', 'rhyme_project', 'data', 'entries_parsed.json')
    if os.path.exists(fallback):
        import shutil
        shutil.copy2(fallback, entries_path)
        print(f"  已从工作区复制: {os.path.getsize(entries_path)//1024}KB")
    else:
        print(f"  ⚠️ entries_parsed.json: 未找到")
        print(f"     需要从仓库 docs 获取或自行解析 entries.yml")
        print(f"     需要从 {ENTRIES_URL} 获取 dieghv 字典后解析")
        all_ok = False

if not all_ok:
    print("\n❌ 缺少原始数据文件，请先下载后再运行。")
    sys.exit(1)
else:
    print("\n✅ 原始数据齐全\n")


# ═════════════════════════════════════════════
# 步骤 1：加载平水韵 + 词林正韵
# ═════════════════════════════════════════════

print("[1/4] 加载韵书数据...")

with open(os.path.join(RAW, 'Pingshui_Rhyme.json'), 'r') as f:
    ps_raw = json.load(f)

PSY_RHYME_CHARS = defaultdict(set)
for sec, rhymes_dict in ps_raw.items():
    for rname, char_list in rhymes_dict.items():
        clean = rname.replace('入声','') if rname.startswith('入声') else rname
        for ch in char_list:
            PSY_RHYME_CHARS[clean].add(ch)
PSY_RHYME_CHARS['三讲'] = set()
ALL_RHYMES = list(PSY_RHYME_CHARS.keys())
print(f"  平水韵: {len(ALL_RHYMES)}韵, {len(set(PSY_RHYME_CHARS.keys()))} 去重")

with open(os.path.join(RAW, 'Cilin_Rhyme.json'), 'r') as f:
    cl_raw = json.load(f)

CILIN_PSY = {
    '第一部': ['一东','二冬','一董','二肿','一送','二宋'],
    '第二部': ['三江','七阳','三讲','二十二养','三绛','二十三漾'],
    '第三部': ['四支','五微','八齐','十灰','四纸','五尾','八荠','十贿','四寘','五未','八霁','十一队'],
    '第四部': ['六鱼','七虞','六语','七麌','六御','七遇'],
    '第五部': ['九佳','十灰','九蟹','十贿','九泰','十卦','十一队'],
    '第六部': ['十一真','十二文','十三元','十一轸','十二吻','十三阮','十二震','十三问','十四愿'],
    '第七部': ['十三元','十四寒','十五删','一先','十三阮','十四旱','十五潸','十六铣','十四愿','十五翰','十六谏','十七霰'],
    '第八部': ['二萧','三肴','四豪','十七筱','十八巧','十九皓','十八啸','十九效','二十号'],
    '第九部': ['五歌','二十哿','二十一个'],
    '第十部': ['六麻','二十一马','二十二祃'],
    '第十一部': ['八庚','九青','十蒸','二十三梗','二十四迥','二十四敬','二十五径'],
    '第十二部': ['十一尤','二十五有','二十六宥'],
    '第十三部': ['十二侵','二十六寝','二十七沁'],
    '第十四部': ['十三覃','十四盐','十五咸','二十七感','二十八琰','二十九豏','二十八勘','二十九艳','三十陷'],
    '第十五部': ['一屋','二沃'],
    '第十六部': ['三觉','十药'],
    '第十七部': ['四质','十一陌','十二锡','十三职','十四缉'],
    '第十八部': ['五物','六月','七曷','八黠','九屑'],
    '第十九部': ['十五合','十六叶','十七洽'],
}
PSY_TO_CILIN = {}
for cl, rlist in CILIN_PSY.items():
    for r in rlist: PSY_TO_CILIN[r] = cl

# ═════════════════════════════════════════════
# 步骤 2：PUJ 韵母 → 平水韵映射规则
# ═════════════════════════════════════════════

print("[2/4] 加载韵母映射规则...")

PUJ_FINAL_TO_PSY = {
    'ong': ['一东','一董','一送','二冬','二肿','二宋'],
    'iong': ['一东','二冬','二肿','二宋'],
    'iok': ['一屋','二沃'],
    'ion': ['七阳','二十二养','二十三漾'],
    'ionn': ['七阳','二十二养'],
    'ok': ['一屋','二沃','三觉','十药'],
    'ang': ['三江','三讲','三绛','七阳','二十二养','十四寒','十四旱','十五翰','十五删','十五潸','一送'],
    'iang': ['三江','三讲','三绛','七阳','二十二养','二十三漾','一先','十六铣','十七霰','八庚','二十三梗'],
    'uang': ['三江','七阳','二十二养','二十三漾','十三元','十三阮','十四愿','十四寒','十四旱','十五翰','十五删','十五潸','十六谏','一先','十六铣','十七霰'],
    'i': ['四支','四纸','四寘','五微','五尾','五未','八齐','八荠','八霁'],
    'ui': ['四支','四纸','四寘','五微','五尾','五未','十灰','十贿','十一队'],
    'v': ['四支','四纸','四寘','六鱼','六语','六御'],
    'ur': ['四支','六鱼','六语','六御'],
    'urn': ['十二文','十二吻','十三问'],
    'urng': ['十二文'],
    'urt': ['五物'],
    'u': ['六鱼','七虞','七麌','七遇','六语','六御','十一尤'],
    'ou': ['七虞','七麌','七遇','四豪','十一尤','二十五有','二十六宥'],
    'eu': ['十一尤','二十五有'],
    'ai': ['九佳','九蟹','十卦','九泰','十灰','十贿','十一队','四支'],
    'ue': ['十灰','十贿','十一队','九泰','五歌','二十哿'],
    'oi': ['十灰','十贿'],
    'uai': ['九佳','十卦'],
    'auh': ['九泰','十卦'],
    'eng': ['十一真','十一轸','十二震','八庚','二十三梗','二十四敬','九青','二十四迥','二十五径','十蒸'],
    'ung': ['十一真','十一轸','十二震','十二文','十二吻','十三问','十三元','十三阮','十四愿','十蒸'],
    'en': ['八庚','二十三梗','二十四敬'],
    'ueng': ['九青','二十四迥','二十五径'],
    'ian': ['一先','十六铣','十七霰','八庚','二十三梗','九青'],
    'iann': ['八庚','六麻'],
    'in': ['一先','十六铣','十七霰','十一真','十一轸','十二震'],
    'inn': ['一先','四支','五微','八庚'],
    'un': ['十二文','十二吻','十三问','十三元','十三阮','十四愿'],
    'an': ['十四寒','十四旱','十五翰','十三元','十三阮','十四愿','十三覃','二十七感','二十八勘'],
    'ann': ['三江','六麻'],
    'uan': ['十四寒','十四旱','十五翰','十三元','十三阮'],
    'uann': ['十四寒','十五翰','七阳','六麻'],
    'ain': ['十五删','十五潸','十六谏'],
    'ainn': ['十五删','十六谏'],
    'oinn': ['一先'],
    'uainn': ['十五删'],
    'uin': ['一先'],
    'uinn': ['一先'],
    'uoinn': ['一先'],
    'it': ['四质'],
    'ut': ['五物','六月'],
    'ek': ['四质','十一陌','十二锡','十三职','一屋','二沃'],
    'uk': ['四质','五物','六月','一屋'],
    'uak': ['六月','七曷','八黠'],
    'iak': ['四质','九屑','十药','十一陌'],
    'uek': ['十三职'],
    'iat': ['九屑','十六叶'],
    'uat': ['六月','七曷','八黠','九屑'],
    'uap': ['十七洽'],
    'ak': ['七曷','八黠','三觉','十药','一屋'],
    'uh': ['六月','七曷'],
    'ueh': ['六月','九屑','七曷'],
    'uah': ['六月','七曷','十药'],
    'oih': ['七曷'],
    'ih': ['九屑','四质'],
    'eh': ['十一陌','十二锡','九屑'],
    'urh': ['五物'],
    'orh': ['十药','三觉'],
    'iap': ['九屑','十六叶','十四缉','十七洽'],
    'iau': ['二萧','十七筱','十八啸','三肴','十八巧','十九效'],
    'iauh': ['二萧'],
    'au': ['三肴','十八巧','十九效','四豪','十九皓','二十号','十一尤','二十五有'],
    'io': ['二萧','十七筱','十八啸'],
    'iaunn': ['二萧'],
    'o': ['五歌','二十哿','二十一个','四豪','十九皓','二十号','七虞','七麌','七遇'],
    'ua': ['五歌','二十哿','二十一个','六麻','二十一马','二十二祃'],
    'ue': ['五歌','二十哿'],
    'or': ['五歌','二十哿'],
    'a': ['六麻','二十一马','二十二祃','三肴'],
    'ia': ['六麻','二十一马','二十二祃'],
    'e': ['八齐','九佳','九蟹','十卦','六麻','二十一马'],
    'enn': ['六麻','八庚','九青'],
    'onn': ['六麻','七阳'],
    'oh': ['十药','三觉'],
    'ioh': ['十一陌','十药'],
    'iah': ['十一陌'],
    'iu': ['十一尤','二十五有','二十六宥'],
    'iuh': ['十一尤'],
    'im': ['十二侵','二十六寝','二十七沁','十四盐','二十八琰'],
    'ip': ['十四缉'],
    'iurm': ['十二侵','十四盐'],
    'am': ['十三覃','二十七感','二十八勘','十五咸','二十九豏','三十陷'],
    'iam': ['十四盐','二十八琰','二十九艳','十五咸','二十九豏','一先','十六铣'],
    'uam': ['十五咸','二十九豏'],
    'ap': ['十五合','十七洽'],
    'ah': ['十五合','十七洽'],
    'ng': ['一东','二冬','七阳','十二侵','七虞','七麌'],
    'n': ['七阳','十二侵'],
    'm': ['十二侵'],
    'ngh': ['三江','七阳'],
    'iunnh': ['七阳'],
}

PSY_TO_PUJ = defaultdict(set)
for fin, rhymes in PUJ_FINAL_TO_PSY.items():
    for r in rhymes: PSY_TO_PUJ[r].add(fin)

# ═════════════════════════════════════════════
# 步骤 3：加载潮汕音数据
# ═════════════════════════════════════════════

print("[3/4] 加载潮汕音数据...")

_PUJ_SPLIT = re.compile(r'^([^aeiou]*)([aeiou][a-z]*)([1-8])$')

def parse_rime_dict(path):
    """解析 RIME 格式字典 (.dict.yaml)"""
    result = {}
    with open(path) as f:
        in_data = False
        for line in f:
            line = line.rstrip()
            if line == '...':
                in_data = True
                continue
            if not in_data or not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                ch = parts[0]
                if len(ch) != 1 or ord(ch) <= 0x2000:
                    continue
                puj = parts[1]
                m = _PUJ_SPLIT.match(puj)
                if m:
                    fin = m.group(2)
                    if ch not in result:
                        result[ch] = set()
                    result[ch].add(fin)
    return result

# 潮州 & 揭阳 口音
cz_readings = parse_rime_dict(os.path.join(RAW, 'dieziu.dict.yaml'))
jy_readings = parse_rime_dict(os.path.join(RAW, 'gekion.dict.yaml'))
print(f"  潮州音: {len(cz_readings)} 字")
print(f"  揭阳音: {len(jy_readings)} 字")

# entries_parsed.json（含文读标注）
with open(os.path.join(RAW, 'entries_parsed.json'), 'r') as f:
    entries_raw = json.load(f)

entries = {}
for ch, readings in entries_raw.items():
    fins = set()
    wen_fins = set()
    for r in readings:
        fin = r['fin']
        fins.add(fin)
        if r.get('wb') == 2:
            wen_fins.add(fin)
    if fins:
        entries[ch] = {'fins': fins, 'wen_fins': wen_fins}

print(f"  entries: {len(entries)} 字")

def get_fins(char, accent_dict):
    """获取某字的最佳韵母集（填词用途：优先文读）"""
    if char in entries:
        e = entries[char]
        if e['wen_fins']:
            return e['wen_fins'], '文读'
        else:
            return e['fins'], '首读'
    if char in accent_dict:
        return accent_dict[char], '口音字典'
    return set(), '无读音'

# ═════════════════════════════════════════════
# 步骤 4：生成古韵→韵母对照 CSV
# ═════════════════════════════════════════════

print("[4/4] 生成对照表 & 交互页面...")

SEC_MAP = {}
for sname, slist in [('上平',['一东','二冬','三江','四支','五微','六鱼','七虞','八齐','九佳','十灰','十一真','十二文','十三元','十四寒','十五删']),
    ('下平',['一先','二萧','三肴','四豪','五歌','六麻','七阳','八庚','九青','十蒸','十一尤','十二侵','十三覃','十四盐','十五咸']),
    ('上声',['一董','二肿','三讲','四纸','五尾','六语','七麌','八荠','九蟹','十贿','十一轸','十二吻','十三阮','十四旱','十五潸','十六铣','十七筱','十八巧','十九皓','二十哿','二十一马','二十二养','二十三梗','二十四迥','二十五有','二十六寝','二十七感','二十八琰','二十九豏']),
    ('去声',['一送','二宋','三绛','四寘','五未','六御','七遇','八霁','九泰','十卦','十一队','十二震','十三问','十四愿','十五翰','十六谏','十七霰','十八啸','十九效','二十号','二十一个','二十二祃','二十三漾','二十四敬','二十五径','二十六宥','二十七沁','二十八勘','二十九艳','三十陷']),
    ('入声',['一屋','二沃','三觉','四质','五物','六月','七曷','八黠','九屑','十药','十一陌','十二锡','十三职','十四缉','十五合','十六叶','十七洽'])]:
    for r in slist: SEC_MAP[r] = sname

for accent_name, accent_dict, label in [
    ('chaozhou', cz_readings, '潮州音'),
    ('jieyang', jy_readings, '揭阳音'),
]:
    csv_path = os.path.join(DATA, f'rhyme_by_rhyme_{accent_name}.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['平水韵韵部','声调','词林正韵部','潮汕音韵母','此韵母归此韵的字','同读此韵母但不属此韵的字','韵母匹配度'])
        
        for rhyme in ALL_RHYMES:
            chars_in_rhyme = PSY_RHYME_CHARS.get(rhyme, set())
            if not chars_in_rhyme:
                continue
            cilin = PSY_TO_CILIN.get(rhyme, '')
            sec = SEC_MAP.get(rhyme, '')
            
            fin_data = defaultdict(lambda: {'in': [], 'outside': []})
            for ch in chars_in_rhyme:
                use_fins, _ = get_fins(ch, accent_dict)
                for fin in use_fins:
                    fin_data[fin]['in'].append(ch)
            
            if not fin_data:
                w.writerow([rhyme, sec, cilin, '(无对应)', '', '', ''])
                continue
            
            for fin in sorted(fin_data.keys()):
                chars_here = fin_data[fin]['in']
                outsiders = []
                for test_char in entries:
                    if test_char not in chars_in_rhyme and fin in entries[test_char]['fins']:
                        outsiders.append(test_char)
                for test_char in accent_dict:
                    if test_char not in chars_in_rhyme and test_char not in outsiders and fin in accent_dict[test_char]:
                        outsiders.append(test_char)
                
                all_cnt = len(chars_here) + len(outsiders)
                match_pct = f"{len(chars_here)}/{all_cnt}" if all_cnt > 0 else "0/0"
                
                w.writerow([
                    rhyme, sec, cilin, fin,
                    ''.join(chars_here),
                    ''.join(outsiders[:30]) + ('…' if len(outsiders) > 30 else ''),
                    match_pct,
                ])
    
    print(f"  → {csv_path}")

# ═════════════════════════════════════════════
# 步骤 5：生成 HTML + data.js
# ═════════════════════════════════════════════

# 重新读 CSV（需含 lookup 数据）
lookup_data = {}
for rhyme in ALL_RHYMES:
    chars = PSY_RHYME_CHARS.get(rhyme, set())
    for ch in chars:
        if ch not in lookup_data:
            lookup_data[ch] = {'r': rhyme, 's': SEC_MAP.get(rhyme, ''), 'c': PSY_TO_CILIN.get(rhyme, '')}

# 词林正韵合并数据
def merge_rd(rd_data, psy_rhymes):
    merged = {}
    for r in psy_rhymes:
        if r not in rd_data: continue
        for fin, info in rd_data[r].items():
            if fin not in merged: merged[fin] = {'in': [], 'outside': []}
            for ch in info['in']:
                if ch not in merged[fin]['in']: merged[fin]['in'].append(ch)
            for ch in info['outside']:
                if ch not in merged[fin]['outside'] and ch not in merged[fin]['in']: merged[fin]['outside'].append(ch)
    return merged

# 加载刚生成的 CSV
def load_csv_rd(path):
    data = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            r = row['平水韵韵部']
            fin = row['潮汕音韵母']
            ins = [c for c in row['此韵母归此韵的字'] if c and ord(c) > 0x2000]
            outs = [c for c in row['同读此韵母但不属此韵的字'] if c and ord(c) > 0x2000]
            if r not in data: data[r] = {}
            data[r][fin] = {'in': ins, 'outside': outs}
    return data

rd_cz = load_csv_rd(os.path.join(DATA, 'rhyme_by_rhyme_chaozhou.csv'))
rd_jy = load_csv_rd(os.path.join(DATA, 'rhyme_by_rhyme_jieyang.csv'))

cilin_cz = {g: merge_rd(rd_cz, rhymes) for g, rhymes in CILIN_PSY.items()}
cilin_jy = {g: merge_rd(rd_jy, rhymes) for g, rhymes in CILIN_PSY.items()}

def safe_json(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return s.replace("'", "\\'").replace('</script>', '<\\/script>')

# 写 data.js
data_js = f'''var _RD_CZ = JSON.parse('{safe_json(rd_cz)}');
var _RD_JY = JSON.parse('{safe_json(rd_jy)}');
var _CILIN_CZ = JSON.parse('{safe_json(cilin_cz)}');
var _CILIN_JY = JSON.parse('{safe_json(cilin_jy)}');
var _SM = JSON.parse('{safe_json(SEC_MAP)}');
var _CG = JSON.parse('{safe_json(CILIN_PSY)}');
var _CT = JSON.parse('{safe_json(PSY_TO_CILIN)}');
var _CL = JSON.parse('{safe_json(lookup_data)}');
'''

with open(os.path.join(OUT, 'data.js'), 'w', encoding='utf-8') as f:
    f.write(data_js)

# 写 index.html
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>潮汕音填词押韵查询</title>
<script src="data.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'Hiragino Sans SC','Noto Sans SC',sans-serif;background:#f0f2f5;color:#333;max-width:960px;margin:0 auto;padding:12px}
.hd{background:linear-gradient(135deg,#1a237e,#283593);color:#fff;padding:20px;border-radius:12px;margin-bottom:12px}
.hd h1{font-size:20px}.hd p{font-size:13px;opacity:.8;margin-top:2px}
.cd{background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.sr{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.sr input{flex:1;min-width:100px;padding:9px 12px;font-size:15px;border:2px solid #d0d0d0;border-radius:8px;outline:none}
.sr input:focus{border-color:#3949ab}
.sr select{padding:9px 10px;font-size:14px;border:2px solid #d0d0d0;border-radius:8px;background:#fff}
.sr button{padding:9px 20px;background:#3949ab;color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer;font-weight:600}
.sr button:hover{background:#283593}
.rh{display:inline-block;padding:3px 10px;border-radius:16px;font-size:13px;cursor:pointer;margin:2px;color:#283593;border:1px solid transparent}
.rh:hover{background:#e8eaf6}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;margin-left:5px;vertical-align:middle}
.sec{font-size:12px;color:#888;margin:8px 0 3px}
.fin{background:#fafafa;border:1px solid #e8e8e8;border-radius:8px;margin-bottom:5px;overflow:hidden}
.fh{padding:8px 12px;background:#f5f5f5;font-size:14px;font-weight:600;cursor:pointer;display:flex;justify-content:space-between;align-items:center;user-select:none}
.fh:hover{background:#eee}
.fb{padding:8px 12px;display:none}
.fin.open .fb{display:block}
.cg{margin-bottom:6px}
.cgl{font-size:12px;color:#777;margin-bottom:3px}
.ct{display:inline-block;padding:1px 5px;margin:1px;border-radius:3px;font-size:14px;cursor:pointer}
.ct:hover{opacity:.8}
.g{background:#c8e6c9;color:#1b5e20}
.r{background:#ffcdd2;color:#b71c1c}
.cnt{font-size:12px;color:#999}
.empty{text-align:center;padding:30px;color:#aaa}.empty .bi{font-size:40px}
.ft{text-align:center;padding:16px;color:#999;font-size:11px}
</style>
</head>
<body>
<div class="hd">
<h1>🔬 潮汕音填词押韵查询</h1>
<p>输入一字 → 定位古韵 → 查看潮汕音押韵范围</p>
</div>

<div class="cd">
<div class="sr">
<input type="text" id="q" placeholder="输入汉字，如「村」「东」「月」…" maxlength="2">
<select id="m"><option value="p">平水韵</option><option value="c">词林正韵</option></select>
<select id="a"><option value="cz">潮州口音</option><option value="jy">揭阳口音</option></select>
<button onclick="go()">查询</button>
</div>
</div>

<div class="cd" id="rhyBar" style="display:none"><div id="rhyBarContent"></div></div>
<div class="cd" id="bw"><div style="font-size:13px;color:#666;margin-bottom:4px">📖 浏览韵部：</div><div id="allRhy"></div></div>
<div class="cd" id="rs" style="display:none"><div id="rc"></div></div>
<div class="ft">潮州/揭阳口音 · 多音文读优先 · 10,055字</div>

<script>
function go() {
    var q=document.getElementById('q').value.trim(); if(!q)return;
    var mode=document.getElementById('m').value;
    var e=_CL[q]; if(!e){document.getElementById('rhyBar').style.display='none';showRes('<div class="empty"><div class="bi">🔍</div><p>未查到「'+q+'」</p></div>');return;}
    if(mode==='p'){document.getElementById('rhyBar').style.display='none';showRhyme(e.r);}
    else {
        var groups=[]; for(var g in _CG){if(_CG[g].indexOf(e.r)>=0)groups.push(g);}
        if(groups.length===0){document.getElementById('rhyBar').style.display='none';showRhyme(e.r);return;}
        var clGroup=groups[0];
        var html='<div style="font-weight:600;font-size:14px;margin-bottom:4px">【'+q+'】词林正韵：</div>';
        for(var gi=0;gi<groups.length;gi++){
            var g=groups[gi],rl=_CG[g];html+='<div style="font-size:12px;font-weight:600;color:#555;margin:5px 0 2px">'+g+'</div>';
            for(var ri=0;ri<rl.length;ri++){
                var r=rl[ri],rd=(document.getElementById('a').value==='cz'?_RD_CZ:_RD_JY);if(!rd[r])continue;
                var has=false;for(var f in rd[r]){if(rd[r][f].in.indexOf(q)>=0){has=true;break;}}
                html+='<span class="rh'+(has?'" style="border:2px solid #3949ab':'')+'" onclick="showRhyme(\\''+r+'\\')">'+r+'</span>';}}
        document.getElementById('rhyBarContent').innerHTML=html;
        document.getElementById('rhyBar').style.display='block';
        document.getElementById('rs').style.display='block';
        showRhyme(clGroup);
    }
}
function showRhyme(rhyme) {
    var mode=document.getElementById('m').value,accent=document.getElementById('a').value;
    var rd;if(mode==='c'){rd=accent==='cz'?_CILIN_CZ:_CILIN_JY;}else{rd=accent==='cz'?_RD_CZ:_RD_JY;}
    var d=rd[rhyme];if(!d)return;
    var sec=mode==='c'?'词林正韵':(_SM[rhyme]||'');var cilin=mode==='c'?rhyme:(_CT[rhyme]||'');
    var tc=({'上平':'#e3f2fd','下平':'#e8f5e9','上声':'#fff3e0','去声':'#fce4ec','入声':'#f3e5f5'})[sec]||'';
    var fins=Object.keys(d).sort(function(a,b){return d[b].in.length-d[a].in.length;});
    var html='<div style="font-size:18px;font-weight:700;margin-bottom:6px;padding-bottom:6px;border-bottom:2px solid #e8eaf6">';
    html+='『'+rhyme+'』<span class="tag" style="background:'+tc+'">'+sec+'</span>';
    if(cilin)html+='<span class="tag" style="background:#e8f5e9;color:#2e7d32">'+cilin+'</span>';
    html+='</div><div style="font-size:12px;color:#888;margin-bottom:8px">共 '+fins.length+' 个韵母</div>';
    for(var fi=0;fi<fins.length;fi++){
        var fin=fins[fi],info=d[fin];var ins=info.in||[],outs=info.outside||[];
        var total=ins.length+outs.length,pct=total>0?(ins.length/total*100):0;
        var pc=pct>50?'#1b5e20':(pct>10?'#e65100':'#b71c1c');
        html+='<div class="fin" id="fc'+fi+'"><div class="fh" onclick="document.getElementById(\\'fc'+fi+'\\').classList.toggle(\\'open\\')">';
        html+='<span style="color:'+pc+';font-family:monospace;font-size:15px">/'+fin+'/</span>';
        html+='<span><span class="cnt">本韵'+ins.length+'字 · 别韵'+outs.length+'字 · '+Math.round(pct)+'%</span><span style="margin-left:6px">▾</span></span></div>';
        html+='<div class="fb"><div class="cg"><div class="cgl">✅ 归此韵（可放心用）</div>';
        for(var ci=0;ci<ins.length;ci++){html+='<span class="ct g" onclick="setQ(\\''+ins[ci]+'\\')">'+ins[ci]+'</span>';}
        html+='</div>';
        if(outs.length>0){
            html+='<div class="cg"><div class="cgl">⚠️ 同音不归此韵（勿混入）</div>';
            for(var ci=0;ci<outs.length;ci++){html+='<span class="ct r" onclick="setQ(\\''+outs[ci]+'\\')">'+outs[ci]+'</span>';}
            html+='</div>';}
        html+='</div></div>';
    }
    showRes(html);
}
function showRes(html){document.getElementById('rc').innerHTML=html;document.getElementById('rs').style.display='block';}
function setQ(ch){document.getElementById('q').value=ch;go();}
function renderAll(){
    var tl=['上平','下平','上声','去声','入声'],ti=['↗','↘','↑','↓','▪'],tc=['#e3f2fd','#e8f5e9','#fff3e0','#fce4ec','#f3e5f5'];
    var tg={上平:[],下平:[],上声:[],去声:[],入声:[]};
    for(var r in(document.getElementById('a').value==='cz'?_RD_CZ:_RD_JY)){var s=_SM[r]||'';if(tg[s])tg[s].push(r);}
    for(var s in tg)tg[s].sort();var html='';
    for(var i=0;i<tl.length;i++){var list=tg[tl[i]]||[];if(!list.length)continue;
        html+='<div class="sec">'+ti[i]+' '+tl[i]+'</div><div style="display:flex;flex-wrap:wrap;gap:4px">';
        for(var ri=0;ri<list.length;ri++){html+='<span class="rh" style="background:'+tc[i]+'!important;color:#333;font-weight:600" onclick="showRhyme(\\''+list[ri]+'\\')">'+list[ri]+'</span>';}
        html+='</div>';}
    document.getElementById('allRhy').innerHTML=html;
}
document.getElementById('a').addEventListener('change',function(){renderAll();});
document.getElementById('q').addEventListener('keydown',function(e){if(e.key==='Enter')go();});
renderAll();
</script>
</body>
</html>'''

with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)

# 生成独立单文件版
with open(os.path.join(OUT, 'index.html'), 'r') as f:
    index_html = f.read()
standalone = index_html.replace('<script src="data.js"></script>', f'<script>{data_js}</script>')
with open(os.path.join(OUT, 'rhyme_tool_standalone.html'), 'w', encoding='utf-8') as f:
    f.write(standalone)

print(f"\n  → {os.path.join(OUT, 'data.js')} ({os.path.getsize(os.path.join(OUT, 'data.js'))//1024}KB)")
print(f"  → {os.path.join(OUT, 'index.html')} ({os.path.getsize(os.path.join(OUT, 'index.html'))//1024}KB)")
print(f"  → {os.path.join(OUT, 'rhyme_tool_standalone.html')} ({os.path.getsize(os.path.join(OUT, 'rhyme_tool_standalone.html'))//1024}KB)")

print("\n" + "=" * 60)
print("✅ 全部完成！")
print("=" * 60)
print(f"\n最终交付物:")
print(f"  {OUT}/rhyme_tool_standalone.html  — 独立单文件（下载双击即用）")
print(f"  {OUT}/index.html                  — 依赖 data.js 的版本")
print(f"  {OUT}/data.js                     — 数据文件")
print(f"")
print(f"复现方式:")
print(f"  1. 下载原始数据到 raw/ 目录")
print(f"  2. python3 build_all.py")