#!/usr/bin/env python3
"""
生成交互式填词押韵查询工具（HTML） — 自包含单页
功能：
  1. 输入一个字 → 定位其古韵部
  2. 选择平水韵/词林正韵
  3. 显示该韵部的潮汕音韵母列表
  4. 每个韵母显示：在此韵的字 / 同音不同韵的字
"""
import json, csv, re

CSV_PATH = '/home/caijunyu/.openclaw/agents/cs-sage/ws/chaoshan_rhyme_deliverables/rhyme_by_rhyme_chaozhou.csv'
LOOKUP_PATH = '/home/caijunyu/.openclaw/agents/cs-sage/ws/chaoshan_rhyme_deliverables/rhyme_lookup_chaozhou.csv'
OUTPUT = '/home/caijunyu/.openclaw/agents/cs-sage/ws/chaoshan_rhyme_deliverables/rhyme_tool.html'

# 1. 加载数据：古韵 -> 韵母信息
rhyme_data = {}  # {rhyme: {fin: {in: [...], outside: [...]}, ...}}
with open(CSV_PATH) as f:
    for row in csv.DictReader(f):
        r = row['平水韵韵部']
        fin = row['潮汕音韵母']
        ins = row['此韵母归此韵的字'].strip()
        outs = row['同读此韵母但不属此韵的字'].strip().rstrip('…')
        
        if r not in rhyme_data:
            rhyme_data[r] = {}
        rhyme_data[r][fin] = {
            'in': [c for c in ins if c and ord(c) > 0x2000],
            'outside': [c for c in outs if c and ord(c) > 0x2000]
        }

# 2. 加载 lookup：字 -> (韵部, PUJ, 词林正韵)
char_lookup = {}  # {char: {rhyme, puj, cilin}}
with open(LOOKUP_PATH) as f:
    for row in csv.DictReader(f):
        ch = row['汉字']
        puj = row['潮汕音(PUJ)']
        rr = row['平水韵']
        sec = row['声调']
        cl = row['词林正韵']
        # 取韵母部分（去掉声母和声调数字）
        fin = re.sub(r'^[^aeiou]*([aeiou][a-z]*)\d$', r'\1', puj) if re.search(r'\d', puj) else ''
        if rr and rr != '(无)':
            char_lookup[ch] = {'rhyme': rr, 'sec': sec, 'cilin': cl, 'puj': puj, 'fin': fin}

# 3. 词林正韵 -> 韵部列表
cilin_rhymes = {
    '第一部(东冬钟)': ['一东','二冬','一董','二肿','一送','二宋'],
    '第二部(江阳唐)': ['三江','七阳','三讲','二十二养','三绛','二十三漾'],
    '第三部(支微齐灰)': ['四支','五微','八齐','十灰','四纸','五尾','八荠','十贿','四寘','五未','八霁','十一队'],
    '第四部(鱼虞模)': ['六鱼','七虞','六语','七麌','六御','七遇'],
    '第五部(佳灰)': ['九佳','十灰','九蟹','十贿','九泰','十卦','十一队'],
    '第六部(真文元)': ['十一真','十二文','十三元','十一轸','十二吻','十三阮','十二震','十三问','十四愿'],
    '第七部(元寒删先)': ['十三元','十四寒','十五删','一先','十三阮','十四旱','十五潸','十六铣','十四愿','十五翰','十六谏','十七霰'],
    '第八部(萧肴豪)': ['二萧','三肴','四豪','十七筱','十八巧','十九皓','十八啸','十九效','二十号'],
    '第九部(歌戈)': ['五歌','二十哿','二十一个'],
    '第十部(麻)': ['六麻','二十一马','二十二祃'],
    '第十一部(庚青蒸)': ['八庚','九青','十蒸','二十三梗','二十四迥','二十四敬','二十五径'],
    '第十二部(尤)': ['十一尤','二十五有','二十六宥'],
    '第十三部(侵)': ['十二侵','二十六寝','二十七沁'],
    '第十四部(覃盐咸)': ['十三覃','十四盐','十五咸','二十七感','二十八琰','二十九豏','二十八勘','二十九艳','三十陷'],
    '第十五部(屋沃)': ['一屋','二沃'],
    '第十六部(觉药)': ['三觉','十药'],
    '第十七部(质陌锡职缉)': ['四质','十一陌','十二锡','十三职','十四缉'],
    '第十八部(物月曷黠屑)': ['五物','六月','七曷','八黠','九屑'],
    '第十九部(合洽)': ['十五合','十六叶','十七洽'],
}

# 4. 声调映射
sec_map = {}
for sname, slist in [('上平',['一东','二冬','三江','四支','五微','六鱼','七虞','八齐','九佳','十灰','十一真','十二文','十三元','十四寒','十五删']),
    ('下平',['一先','二萧','三肴','四豪','五歌','六麻','七阳','八庚','九青','十蒸','十一尤','十二侵','十三覃','十四盐','十五咸']),
    ('上声',['一董','二肿','三讲','四纸','五尾','六语','七麌','八荠','九蟹','十贿','十一轸','十二吻','十三阮','十四旱','十五潸','十六铣','十七筱','十八巧','十九皓','二十哿','二十一马','二十二养','二十三梗','二十四迥','二十五有','二十六寝','二十七感','二十八琰','二十九豏']),
    ('去声',['一送','二宋','三绛','四寘','五未','六御','七遇','八霁','九泰','十卦','十一队','十二震','十三问','十四愿','十五翰','十六谏','十七霰','十八啸','十九效','二十号','二十一个','二十二祃','二十三漾','二十四敬','二十五径','二十六宥','二十七沁','二十八勘','二十九艳','三十陷']),
    ('入声',['一屋','二沃','三觉','四质','五物','六月','七曷','八黠','九屑','十药','十一陌','十二锡','十三职','十四缉','十五合','十六叶','十七洽'])]:
    for r in slist:
        sec_map[r] = sname

# 5. 构建词林正韵反向映射
cilin_to_psy = {}
for cl_name, psy_list in cilin_rhymes.items():
    for p in psy_list:
        cilin_to_psy[p] = cl_name

# 6. 生成所有韵部、所有口音信息（合并到一个JS数据结构里）
all_rhymes = sorted(rhyme_data.keys())

# 构建词林正韵分组信息
cilin_groups = {k: v for k, v in cilin_rhymes.items()}

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>潮汕音填词押韵查询工具</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, 'Noto Sans SC', 'Microsoft YaHei', sans-serif; 
       background: #f5f5f5; color: #333; max-width: 900px; margin: 0 auto; padding: 16px; }
.header { background: linear-gradient(135deg, #1a237e, #283593); color: #fff; 
          padding: 24px; border-radius: 12px; margin-bottom: 16px; }
.header h1 { font-size: 22px; margin-bottom: 4px; }
.header p { font-size: 13px; opacity: .85; }
.search-section { background: #fff; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
.search-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.search-row input { flex: 1; min-width: 120px; padding: 10px 14px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; outline: none; }
.search-row input:focus { border-color: #3949ab; }
.search-row select { padding: 10px 14px; font-size: 15px; border: 2px solid #ddd; border-radius: 8px; background: #fff; outline: none; }
.search-row button { padding: 10px 24px; background: #3949ab; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; }
.search-row button:hover { background: #283593; }
.rhyme-select-section { background: #fff; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
.rhyme-select-section label { font-size: 14px; color: #666; margin-right: 8px; }
.rhyme-badge { display: inline-block; padding: 4px 12px; background: #e8eaf6; color: #283593; border-radius: 20px; font-size: 13px; cursor: pointer; margin: 3px; }
.rhyme-badge:hover { background: #c5cae9; }
.rhyme-badge.active { background: #3949ab; color: #fff; }
.result-section { background: #fff; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.1); display: none; }
.result-header { font-size: 18px; font-weight: 700; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #e8eaf6; }
.result-header .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 8px; }
.tag-tone { background: #e3f2fd; color: #1565c0; }
.tag-cilin { background: #e8f5e9; color: #2e7d32; }
.fin-card { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 8px; overflow: hidden; }
.fin-card-header { padding: 10px 14px; background: #f5f5f5; font-weight: 700; font-size: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.fin-card-header:hover { background: #eee; }
.fin-card-body { padding: 10px 14px; display: none; }
.fin-card.open .fin-card-body { display: block; }
.char-group { margin-bottom: 10px; }
.char-group-label { font-size: 12px; color: #666; margin-bottom: 4px; }
.char-tag { display: inline-block; padding: 2px 7px; margin: 2px; border-radius: 4px; font-size: 14px; cursor: pointer; }
.char-tag:hover { opacity: .8; }
.char-in { background: #c8e6c9; color: #1b5e20; }
.char-out { background: #ffcdd2; color: #b71c1c; }
.char-count { font-size: 12px; color: #999; margin-left: 6px; }
.word-search-result { margin-bottom: 10px; }
.word-detail { background: #f5f5f5; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; }
.word-detail .label { font-size: 12px; color: #888; }
.word-detail .val { font-size: 16px; font-weight: 600; }
.result-fins { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.fin-tag { padding: 6px 16px; border-radius: 20px; font-size: 14px; cursor: pointer; transition: .15s; }
.fin-tag.in { background: #c8e6c9; color: #1b5e20; border: 1px solid #a5d6a7; }
.fin-tag.in:hover { background: #a5d6a7; }
.fin-tag.out { background: #ffcdd2; color: #b71c1c; border: 1px solid #ef9a9a; }
.fin-tag.out:hover { background: #ef9a9a; }
.empty-state { text-align: center; padding: 40px; color: #999; }
.empty-state .big { font-size: 48px; margin-bottom: 12px; }
.footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
</style>
</head>
<body>

<div class="header">
<h1>🔬 潮汕音填词押韵查询</h1>
<p>输入一个字 → 定位古韵 → 查看对应的潮汕音押韵范围</p>
</div>

<div class="search-section">
<div class="search-row">
<input type="text" id="charInput" placeholder="输入汉字，如「村」「东」「月」…" maxlength="2">
<select id="modeSelect">
<option value="pingshui">平水韵</option>
<option value="cilin">词林正韵</option>
</select>
<button onclick="search()">查询</button>
</div>
</div>

<div id="rhymeSelectSection" class="rhyme-select-section" style="display:none">
<label>▼ 该字所属古韵 <span id="modeName"></span>：</label>
<div id="rhymeBadges"></div>
</div>

<div id="resultSection" class="result-section">
<div id="resultContent"></div>
</div>

<div id="rhymeBrowseSection" class="rhyme-select-section">
<label>📖 或直接浏览古韵（按声调分组）：</label>
<div id="browseAll"></div>
</div>

<div id="browseResult" class="result-section" style="display:none">
<div id="browseContent"></div>
</div>

<div class="footer">
数据源：teochew-lexicon + dieghv 字典 | 口音：潮州府城音 | 多音优先文读判韵
</div>

<script>
'''

# 嵌入数据
html += 'const RHYME_DATA = ' + json.dumps(rhyme_data, ensure_ascii=False) + ';\n'
html += 'const CHAR_LOOKUP = ' + json.dumps(char_lookup, ensure_ascii=False) + ';\n'
html += 'const SEC_MAP = ' + json.dumps(sec_map, ensure_ascii=False) + ';\n'
html += 'const CILIN_GROUPS = ' + json.dumps(cilin_groups, ensure_ascii=False) + ';\n'
html += 'const CILIN_TO_PSY = ' + json.dumps(cilin_to_psy, ensure_ascii=False) + ';\n'

# 按声调分组韵目
tone_groups = {'上平':[],'下平':[],'上声':[],'去声':[],'入声':[]}
for r in sorted(rhyme_data.keys()):
    s = sec_map.get(r, '')
    if s in tone_groups:
        tone_groups[s].append(r)

html += 'const TONE_GROUPS = ' + json.dumps(tone_groups, ensure_ascii=False) + ';\n'

# 生成所有韵部列表用于反向查找
all_psy = sorted(rhyme_data.keys())
html += 'const ALL_RHYMES = ' + json.dumps(all_psy, ensure_ascii=False) + ';\n'

html += '''
// 平水韵快速查找：给定字，找韵部
function findRhyme(char) {
    const entry = CHAR_LOOKUP[char];
    if (!entry) return null;
    return entry;
}

// 显示模式
let currentMode = 'pingshui';

// 主搜索函数
function search() {
    const char = document.getElementById('charInput').value.trim();
    const mode = document.getElementById('modeSelect').value;
    currentMode = mode;
    
    if (!char) { showToast('请输入汉字'); return; }
    
    const entry = findRhyme(char);
    if (!entry) {
        document.getElementById('rhymeSelectSection').style.display = 'none';
        document.getElementById('resultSection').style.display = 'none';
        showResult('<div class="empty-state"><div class="big">🔍</div><p>未查到「' + char + '」的韵部信息</p><p style="font-size:12px;color:#bbb">该字可能不在韵书中，或潮汕音未收录</p></div>');
        return;
    }
    
    const firstRhyme = entry.rhyme;
    const cilinGroup = CILIN_TO_PSY[firstRhyme] || '';
    
    if (mode === 'pingshui') {
        // 平水韵模式：直接显示这个韵
        document.getElementById('rhymeSelectSection').style.display = 'none';
        document.getElementById('rhymeBrowseSection').innerHTML = '<label>📖 浏览其他韵：</label><div id="browseAll"></div>';
        renderBrowseAll();
        showRhymeDetail(firstRhyme);
    } else {
        // 词林正韵模式：找此字所属的词林正韵组，列出所有韵部
        const groups = [];
        for (const [g, rhymes] of Object.entries(CILIN_GROUPS)) {
            const found = rhymes.find(r => {
                const e = CHAR_LOOKUP[char];
                return e && e.rhyme === r;
            });
            if (found) groups.push(g);
        }
        
        if (groups.length === 0) {
            // 找不到词林正韵归属，回退到平水韵
            document.getElementById('rhymeSelectSection').style.display = 'none';
            showRhymeDetail(firstRhyme);
            return;
        }
        
        // 显示该词林正韵组的所有韵
        document.getElementById('modeName').textContent = '词林正韵';
        const badgesDiv = document.getElementById('rhymeBadges');
        badgesDiv.innerHTML = '';
        document.getElementById('rhymeSelectSection').style.display = 'block';
        
        for (const g of groups) {
            const rhList = CILIN_GROUPS[g] || [];
            // 显示组名
            const groupLabel = document.createElement('div');
            groupLabel.style.cssText = 'font-size:13px;font-weight:600;color:#555;margin:8px 0 4px;';
            groupLabel.textContent = g;
            badgesDiv.appendChild(groupLabel);
            
            for (const r of rhList) {
                if (!RHYME_DATA[r]) continue;
                const badge = document.createElement('span');
                badge.className = 'rhyme-badge';
                badge.textContent = r;
                badge.onclick = () => {
                    document.querySelectorAll('.rhyme-badge').forEach(b => b.classList.remove('active'));
                    badge.classList.add('active');
                    showRhymeDetail(r);
                };
                // 如果这个韵含当前字，高亮
                const rd = RHYME_DATA[r];
                for (const [fin, info] of Object.entries(rd)) {
                    if (info.in.includes(char)) {
                        badge.style.border = '2px solid #3949ab';
                        break;
                    }
                }
                badgesDiv.appendChild(badge);
            }
        }
        
        // 默认选第一个组的第一个韵
        const firstG = groups[0];
        const firstR = (CILIN_GROUPS[firstG] || []).find(r => RHYME_DATA[r]);
        if (firstR) showRhymeDetail(firstR);
    }
}

// 显示单个韵部的详情
function showRhymeDetail(rhyme) {
    const data = RHYME_DATA[rhyme];
    if (!data) { showResult('<div class="empty-state"><p>无「' + rhyme + '」的数据</p></div>'); return; }
    
    const sec = SEC_MAP[rhyme] || '';
    const cilin = CILIN_TO_PSY[rhyme] || '';
    
    const fins = Object.keys(data).sort();
    
    let html = '';
    html += '<div class="result-header">';
    html += '『' + rhyme + '』<span class="tag tag-tone">' + sec + '</span>';
    if (cilin) html += '<span class="tag tag-cilin">' + cilin + '</span>';
    html += '</div>';
    
    html += '<div style="font-size:12px;color:#888;margin-bottom:10px;">';
    html += '<span style="font-weight:600;color:#3949ab;">δ' + fins.length + '</span> 个潮汕音韵母 · ';
    html += '点击"本韵字"跳转到该字详情 · 点击韵母名展开/折叠';
    html += '</div>';
    
    for (const fin of fins) {
        const info = data[fin];
        const ins = info.in || [];
        const outs = info.outside || [];
        const total = ins.length + outs.length;
        const matchInfo = ins.length + '/' + total;
        
        // 计算匹配度颜色
        const pct = total > 0 ? (ins.length / total * 100) : 0;
        const pctColor = pct > 50 ? '#1b5e20' : (pct > 10 ? '#e65100' : '#b71c1c');
        
        // 标签名颜色
        const finColor = pct > 50 ? '#1b5e20' : (pct > 10 ? '#e65100' : '#b71c1c');
        
        html += '<div class="fin-card" id="card-' + fin + '">';
        html += '<div class="fin-card-header" onclick="toggleFinCard(\'' + fin + '\')">';
        html += '<span style="color:' + finColor + '">/ ' + fin + ' /</span>';
        html += '<span><span class="char-count">本韵' + ins.length + '字 · 混入' + outs.length + '字</span>'
        html += '<span style="font-size:12px;color:' + pctColor + ';font-weight:400;margin-left:8px;">纯度' + (pct > 0 ? pct.toFixed(0) : 0) + '%</span>';
        html += '<span style="margin-left:8px;">▾</span></span>';
        html += '</div>';
        
        html += '<div class="fin-card-body">';
        
        // 本韵的字（绿色）
        html += '<div class="char-group">';
        html += '<div class="char-group-label">✅ 本韵字 — 押「' + fin + '」韵可选：</div>';
        for (const ch of ins) {
            html += '<span class="char-tag char-in" onclick="searchChar(\'' + ch + '\')">' + ch + '</span>';
        }
        html += '</div>';
        
        // 混入字（红色）
        if (outs.length > 0) {
            html += '<div class="char-group">';
            html += '<div class="char-group-label">⚠️ 同音不同韵 — 读「' + fin + '」但不在「' + rhyme + '」韵：</div>';
            for (const ch of outs) {
                html += '<span class="char-tag char-out" onclick="searchChar(\'' + ch + '\')">' + ch + '</span>';
            }
            html += '</div>';
        }
        
        html += '</div></div>';
    }
    
    showResult(html);
}

function toggleFinCard(fin) {
    const card = document.getElementById('card-' + fin);
    if (card) card.classList.toggle('open');
}

function showResult(html) {
    document.getElementById('resultContent').innerHTML = html;
    document.getElementById('resultSection').style.display = 'block';
}

function showToast(msg) {
    // Simple toast
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:10px 24px;border-radius:8px;z-index:999;font-size:14px;';
    d.textContent = msg;
    document.body.appendChild(d);
    setTimeout(() => d.remove(), 2000);
}

function searchChar(ch) {
    document.getElementById('charInput').value = ch;
    search();
    document.getElementById('charInput').focus();
    document.getElementById('charInput').setSelectionRange(ch.length, ch.length);
}

// 浏览所有韵部
function renderBrowseAll() {
    const div = document.getElementById('browseAll');
    if (!div) return;
    
    const toneLabels = ['上平', '下平', '上声', '去声', '入声'];
    const toneColors = ['#e3f2fd', '#e8f5e9', '#fff3e0', '#fce4ec', '#f3e5f5'];
    const toneEmojis = ['↗', '↘', '↑', '↓', '▪'];
    
    for (const ti in toneLabels) {
        const tl = toneLabels[ti];
        const list = TONE_GROUPS[tl] || [];
        if (list.length === 0) continue;
        
        const label = document.createElement('div');
        label.style.cssText = 'font-size:12px;color:#888;margin:10px 0 4px;';
        label.textContent = toneEmojis[ti] + ' ' + tl;
        div.appendChild(label);
        
        for (const r of list) {
            const badge = document.createElement('span');
            badge.className = 'rhyme-badge';
            badge.textContent = r;
            badge.style.background = toneColors[ti];
            badge.style.color = '#333';
            badge.style.fontWeight = '600';
            badge.onclick = () => {
                document.getElementById('browseResult').style.display = 'block';
                // Scroll to result
                showRhymeDetail(r);
                document.getElementById('browseResult').scrollIntoView({behavior:'smooth'});
            };
            div.appendChild(badge);
        }
    }
}

// Enter 键搜索
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('charInput').addEventListener('keypress', e => {
        if (e.key === 'Enter') search();
    });
    renderBrowseAll();
});
</script>
</body>
</html>'''

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML 工具已生成: {OUTPUT}")
print(f"文件大小: {len(html.encode('utf-8'))//1024}KB")