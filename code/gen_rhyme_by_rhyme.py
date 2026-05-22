#!/usr/bin/env python3
"""
按古韵反查潮汕音韵母和字表 — 填词创作专用 v2
============================================
这次每列更干净，每个古韵里按潮汕音韵母分多行展示，
一眼看清每个韵母对应哪些字、哪些同音但不同韵。
"""
import json, csv, os, re
from collections import defaultdict

PROJ = '/home/caijunyu/.openclaw/agents/cs-sage/ws/rhyme_project'
DATA = f'{PROJ}/data'
OUT = '/home/caijunyu/.openclaw/agents/cs-sage/ws/chaoshan_rhyme_deliverables'
os.makedirs(OUT, exist_ok=True)

# 1. 平水韵
with open(f'{DATA}/Pingshui_Rhyme.json', 'r') as f:
    ps_raw = json.load(f)
PSY_RHYME_CHARS = defaultdict(set)
for sec, rhymes_dict in ps_raw.items():
    for rname, char_list in rhymes_dict.items():
        clean = rname.replace('入声','') if rname.startswith('入声') else rname
        for ch in char_list:
            PSY_RHYME_CHARS[clean].add(ch)
PSY_RHYME_CHARS['三讲'] = set()
ALL_RHYMES = list(PSY_RHYME_CHARS.keys())

# 2. 词林正韵映射
CILIN_PSY = {
    '第一部(东冬钟)':    ['一东','二冬','一董','二肿','一送','二宋'],
    '第二部(江阳唐)':    ['三江','七阳','三讲','二十二养','三绛','二十三漾'],
    '第三部(支微齐灰)':  ['四支','五微','八齐','十灰','四纸','五尾','八荠','十贿','四寘','五未','八霁','十一队'],
    '第四部(鱼虞模)':    ['六鱼','七虞','六语','七麌','六御','七遇'],
    '第五部(佳灰)':      ['九佳','十灰','九蟹','十贿','九泰','十卦','十一队'],
    '第六部(真文元)':    ['十一真','十二文','十三元','十一轸','十二吻','十三阮','十二震','十三问','十四愿'],
    '第七部(元寒删先)':  ['十三元','十四寒','十五删','一先','十三阮','十四旱','十五潸','十六铣','十四愿','十五翰','十六谏','十七霰'],
    '第八部(萧肴豪)':    ['二萧','三肴','四豪','十七筱','十八巧','十九皓','十八啸','十九效','二十号'],
    '第九部(歌戈)':      ['五歌','二十哿','二十一个'],
    '第十部(麻)':        ['六麻','二十一马','二十二祃'],
    '第十一部(庚青蒸)':  ['八庚','九青','十蒸','二十三梗','二十四迥','二十四敬','二十五径'],
    '第十二部(尤)':      ['十一尤','二十五有','二十六宥'],
    '第十三部(侵)':      ['十二侵','二十六寝','二十七沁'],
    '第十四部(覃盐咸)':  ['十三覃','十四盐','十五咸','二十七感','二十八琰','二十九豏','二十八勘','二十九艳','三十陷'],
    '第十五部(屋沃)':    ['一屋','二沃'],
    '第十六部(觉药)':    ['三觉','十药'],
    '第十七部(质陌锡职缉)': ['四质','十一陌','十二锡','十三职','十四缉'],
    '第十八部(物月曷黠屑)': ['五物','六月','七曷','八黠','九屑'],
    '第十九部(合洽)':    ['十五合','十六叶','十七洽'],
}
PSY_TO_CILIN = {}
for cl, rlist in CILIN_PSY.items():
    for r in rlist:
        PSY_TO_CILIN[r] = cl

# 3. PUJ韵母 -> 平水韵 映射（同前）
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
    for r in rhymes:
        PSY_TO_PUJ[r].add(fin)

# 4. 加载潮汕音读音
_PUJ_SPLIT = re.compile(r'^([^aeiou]*)([aeiou][a-z]*)([1-8])$')

def parse_rime(path):
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

# entries 读音（预解析JSON）
with open(f'{DATA}/entries_parsed.json', 'r') as f:
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

def get_fins(char, accent_dict):
    if char in entries:
        e = entries[char]
        if e['wen_fins']:
            return e['wen_fins'], e['fins'], '文读'
        else:
            return e['fins'], e['fins'], '首读'
    if char in accent_dict:
        return accent_dict[char], accent_dict[char], '口音字典'
    return set(), set(), '无读音'

SEC_MAP = {}
for sname, slist in [('上平',['一东','二冬','三江','四支','五微','六鱼','七虞','八齐','九佳','十灰','十一真','十二文','十三元','十四寒','十五删']),
    ('下平',['一先','二萧','三肴','四豪','五歌','六麻','七阳','八庚','九青','十蒸','十一尤','十二侵','十三覃','十四盐','十五咸']),
    ('上声',['一董','二肿','三讲','四纸','五尾','六语','七麌','八荠','九蟹','十贿','十一轸','十二吻','十三阮','十四旱','十五潸','十六铣','十七筱','十八巧','十九皓','二十哿','二十一马','二十二养','二十三梗','二十四迥','二十五有','二十六寝','二十七感','二十八琰','二十九豏']),
    ('去声',['一送','二宋','三绛','四寘','五未','六御','七遇','八霁','九泰','十卦','十一队','十二震','十三问','十四愿','十五翰','十六谏','十七霰','十八啸','十九效','二十号','二十一个','二十二祃','二十三漾','二十四敬','二十五径','二十六宥','二十七沁','二十八勘','二十九艳','三十陷']),
    ('入声',['一屋','二沃','三觉','四质','五物','六月','七曷','八黠','九屑','十药','十一陌','十二锡','十三职','十四缉','十五合','十六叶','十七洽'])]:
    for r in slist:
        SEC_MAP[r] = sname

print("生成中...")

for accent_name, accent_path, label in [
    ('chaozhou', f'{DATA}/dieghv_dieziu.dict.yaml', '潮州音'),
    ('jieyang', f'{DATA}/dieghv_gekion.dict.yaml', '揭阳音'),
]:
    print(f"  {label}:")
    accent = parse_rime(accent_path)
    
    outpath = f'{OUT}/rhyme_by_rhyme_{accent_name}.csv'
    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            '平水韵韵部', '声调', '词林正韵部',
            '潮汕音韵母',                 # 这个古韵里出现的一个具体韵母
            '此韵母归此韵的字',           # 本韵的字
            '同读此韵母但不属此韵的字',   # 陷阱——同音不同韵
            '韵母匹配度',                 # 这个韵母在该韵中出现的频率
        ])
        
        for rhyme in ALL_RHYMES:
            chars_in_rhyme = PSY_RHYME_CHARS.get(rhyme, set())
            if not chars_in_rhyme:
                continue
            
            cilin = PSY_TO_CILIN.get(rhyme, '')
            sec = SEC_MAP.get(rhyme, '')
            
            # 收集该韵中各潮汕音韵母的信息
            fin_data = defaultdict(lambda: {'in': [], 'outside': []})
            for ch in chars_in_rhyme:
                wen, all_f, src = get_fins(ch, accent)
                use_fins = wen if wen else all_f
                for fin in use_fins:
                    fin_data[fin]['in'].append(ch)
            
            if not fin_data:
                # 这个古韵在潮汕音里没有对应
                w.writerow([rhyme, sec, cilin, '(无对应)', '', '', ''])
                continue
            
            # 对每个韵母，找不在此韵但读此韵母的字
            for fin in sorted(fin_data.keys()):
                chars_here = fin_data[fin]['in']
                # 找第三人称
                outsiders = []
                for test_char in entries:
                    if test_char not in chars_in_rhyme:
                        if fin in entries[test_char]['fins']:
                            outsiders.append(test_char)
                for test_char in accent:
                    if test_char not in chars_in_rhyme and test_char not in outsiders:
                        if fin in accent[test_char]:
                            outsiders.append(test_char)
                
                # 匹配度 = 本韵中此韵母的字数 / 所有读此韵母的总字数
                all_with_fin = len(chars_here) + len(outsiders)
                match_pct = f"{len(chars_here)}/{all_with_fin}" if all_with_fin > 0 else "0/0"
                
                chars_here_disp = "".join(chars_here)
                outsiders_disp = "".join(outsiders[:30]) if outsiders else ''
                if len(outsiders) > 8:
                    outsiders_disp += '…'
                
                w.writerow([
                    rhyme, sec, cilin,
                    fin,
                    chars_here_disp,
                    outsiders_disp,
                    match_pct,
                ])
    
    print(f"    → {outpath}")

print("\n=== 完成 ===")
print("现在查十三元的方法：")
print("  grep '十三元' rhyme_by_rhyme_chaozhou.csv")
print("  每行一个潮汕音韵母，告诉你这个韵母对应本韵哪些字、同音不同韵的有哪些字")