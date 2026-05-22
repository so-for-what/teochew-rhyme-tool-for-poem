# 潮汕音填词押韵查询工具

> **交互式网页工具** | 输入汉字 → 定位古韵 → 查看潮汕话押韵范围

[🔗 GitHub 仓库](https://github.com/so-for-what/teochew-rhyme-tool-for-poem)

---

## 目录

- [快速开始](#快速开始)
- [功能演示](#功能演示)
- [目标受众](#目标受众)
- [项目结构](#项目结构)
- [技术原理](#技术原理)
  - [整体流程](#整体流程)
  - [数据采集](#1-数据采集)
  - [数据处理](#2-数据处理)
  - [交互页面生成](#3-交互页面生成)
- [完整复现步骤](#完整复现步骤)
  - [环境准备](#环境准备)
  - [步骤 1：下载原始数据](#步骤-1下载原始数据)
  - [步骤 2：生成古韵→韵母对照表](#步骤-2生成古韵韵母对照表)
  - [步骤 3：生成交互式网页](#步骤-3生成交互式网页)
  - [步骤 4：使用](#步骤-4使用)
- [数据格式说明](#数据格式说明)
  - [rhyme_by_rhyme CSV](#rhyme_by_rhymecsv-格式)
  - [data.js](./output/data.js)
  - [index.html](./output/index.html)
- [后续拓展指南](#后续拓展指南)
  - [1. 拓展口音](#1-拓展口音)
  - [2. 多音字文白分层](#2-多音字文白分层)
  - [3. 拓展古韵（中华新韵等）](#3-拓展古韵中华新韵等)
  - [4. 增加韵母映射规则](#4-增加韵母映射规则)
  - [5. 拓展为可搜索前端](#5-拓展为可搜索前端)
- [数据来源](#数据来源)
- [许可证](#许可证)

---

## 快速开始

1. 用浏览器打开 [`https://htmlpreview.github.io/?https://github.com/so-for-what/teochew-rhyme-tool-for-poem/blob/main/output/index.html`](https://htmlpreview.github.io/?https://github.com/so-for-what/teochew-rhyme-tool-for-poem/blob/main/output/index.html)（或直接双击文件）

> 如果你想从头重建所有数据，终端运行 `python3 build_all.py` 即可。
2. 输入一个汉字（如「村」「东」「月」）
3. 选择「平水韵」或「词林正韵」
4. 选择「潮州口音」或「揭阳口音」
5. 点击「查询」

页面展示该字所属的古韵，以及对应的所有潮汕话韵母。点击每个韵母卡片可展开，看到：
- ✅ **归此韵的字**（可放心押韵）
- ⚠️ **同韵母但不归此韵的字**（注意勿混入）

韵母卡片按本韵字数从多到少排列。

---

## 功能演示

| 操作 | 效果 |
|------|------|
| 输入"村"，选平水韵 | 显示"十三元"下方列出 /ian/、/uan/、/un/ 等十个韵母卡片 |
| 选词林正韵 | 顶部显示第七部（元寒删先）组内韵部，下方展示合并后的本韵/别韵 |
| 切换揭阳口音 | 数据切换，揭阳不同读法的字单独标注 |
| 展开韵母卡片 | 看到具体哪些字可用、哪些字同音但不同韵 |

---

## 目标受众

- 潮汕人填词赋诗时需要知道：**我读的这个音，在古代属于哪个韵？**
- 以及反过来：**我想押某个古韵，潮汕话里可以用哪些韵母？**

不需要理解中古音韵学，不需要翻韵书，输入汉字即可。

---

## 项目结构

```
.
├── build_all.py                      # 🎯 一键构建（从原始数据到最终文件）
├── README.md                         # 本文件
├── raw/                              # 📥 全部原始数据（已包含，可复现）
│   ├── Pingshui_Rhyme.json           #    平水韵 106 韵
│   ├── Cilin_Rhyme.json              #    词林正韵 19 部
│   ├── character.csv                 #    潮汕音 P0（teochew-lexicon）
│   ├── entries_parsed.json           #    潮汕音 P1（含文白标注）
│   ├── dieziu.dict.yaml              #    潮州音字典
│   └── gekion.dict.yaml              #    揭阳音字典
├── data/                             # 中间数据（build_all.py 生成）
│   ├── rhyme_by_rhyme_chaozhou.csv   #    潮州音：古韵→韵母对照
│   └── rhyme_by_rhyme_jieyang.csv    #    揭阳音：古韵→韵母对照
├── output/                           # 🎯 最终交付物（可直接使用）
│   ├── rhyme_tool_standalone.html    #    独立单文件（下载双击即用）
│   ├── index.html                    #    交互页面（需 data.js）
│   └── data.js                       #    数据文件
└── code/                             # 分步脚本（备选）
    ├── gen_rhyme_by_rhyme.py         #    CSV 生成脚本
    └── gen_tool_html.py              #    HTML 生成脚本
```

---

## 技术原理

### 整体流程

```
原始数据集                    中间数据                     最终交付物
──────────                   ────────                    ─────────
平水韵字表  ──┐
词林正韵字表 ─┤              rhyme_by_rhyme_*.csv         index.html
潮汕音P0    ─┼──►   Python  ────────────────►  Python ──►  + data.js
潮汕音P1    ─┤              （古韵→韵母对照）            （交互页面）
潮汕音P2    ─┘
```

### 1. 数据采集

#### 平水韵 106 韵
| 来源 | 描述 |
|------|------|
| 项目 | `charlesix59/chinese_word_rhyme` |
| 文件 | `data/Pingshui_Rhyme.json` |
| 格式 | JSON（5 部分 → 韵名 → 字列表） |
| 覆盖 | 上平 15 韵 + 下平 15 韵 + 上声 29 韵 + 去声 30 韵 + 入声 17 韵 = **106 韵** |
| 去重字数 | 8,232 |
| 备注 | 入声韵名前缀"入声"在代码中自动去除，缺失的"三讲"韵补全 |

#### 词林正韵 19 部
| 来源 | 描述 |
|------|------|
| 项目 | `charlesix59/chinese_word_rhyme` |
| 文件 | `data/Cilin_Rhyme.json` |
| 格式 | JSON（19 部 → 四声 → 字列表） |
| 覆盖 | **19 部**（平上去 14 部 + 入声 5 部） |
| 去重字数 | 5,037 |

词林正韵与平水韵的对应关系是严格合并：**一部词林正韵 = 若干平水韵韵部的并集，不存在交叉归属。** 例如：
- 第七部（元寒删先）= 十三元 + 十四寒 + 十五删 + 一先 + 阮 + 旱 + 潸 + 铣 + 愿 + 翰 + 谏 + 霰
- 第十五部（屋沃）= 一屋 + 二沃

#### 潮汕音（三个独立数据源）

| 优先级 | 来源 | 内容 | 字数 | 获取方式 |
|--------|------|------|------|---------|
| P0 | `hokkien-writing/teochew-lexicon` | `character.csv`，PUJ 拼音 | 6,169 | CDN 下载 |
| P1 | `hokkien-writing/dataset`（dieghv 字典） | `entries.yml`，含文白读标注 | 9,859 | 解析 YAML |
| P2 | `kahaani/dieghv`（**官方原始仓库**） | `dieziu.dict.yaml`（潮州）、`gekion.dict.yaml`（揭阳） | 7,487 / 7,477 | GitHub 下载 |

**整合方式**：以汉字为 key，三源合并。P1 提供文白读标记（wb=2 文读，wb=1 白读），P2 提供口音差异。P2 贡献了 63 个 P0/P1 未收录的新字。

**总字头：10,055**。

### 2. 数据处理

#### 2a. 潮汕音韵母提取

PUJ（Pe̍h-ōe-jī）拼音的格式是 `声母+韵母+声调数字`，例如 `zek8`：
- RIME 字典格式：`zek8` → 声母=z, 韵母=ek, 声调=8
- 拆分正则：`^([^aeiou]*)([aeiou][a-z]*)([1-8])$`
  - `zek8` → `z` + `ek` + `8` ✅
  - `deng1` → `d` + `eng` + `1` ✅
  - `iou1` → ``（零声母）+ `iou` + `1` ✅

#### 2b. 韵母→古韵映射规则

核心算法：建立从 PUJ 韵母到平水韵韵目的映射表，基于**中古音韵对应规律**。

例如：
- `/ong/` → 一东、二冬（通摄）
- `/ang/` → 三江、七阳、十四寒、十五删
- `/ian/` → 一先、八庚
- `/eng/` → 十一真、八庚、九青、十蒸
- `/ok/` → 一屋、二沃、三觉、十药

完整映射表覆盖 **90 个 PUJ 韵母**。反向索引（韵目→预期韵母）用于判断一个字的潮汕音是否匹配其古韵。

#### 2c. 韵部判韵算法

对每个汉字 **优先取文读（wb=2）** 判韵：

```
1. 查 entries.yml 是否有 wb=2 读音 → 取文读韵母
2. 无文读 → 取首读韵母
3. 查映射表 → 匹配韵部
4. 若韵母不在映射表 → 标记为"韵母偏差"
5. 若字不在韵书 → 标记为"韵书未收录"
```

#### 2d. 词林正韵合并

词林正韵模式下，不是展示单个平水韵韵部的数据，而是**将整个词林正韵部内所有平水韵韵部的字合并**，按韵母重新聚合：

```
第七部 = 十三元 ∪ 十四寒 ∪ 十五删 ∪ 一先 ∪ 阮 ∪ 旱 ∪ 潸 ∪ 铣 ∪ 愿 ∪ 翰 ∪ 谏 ∪ 霰

合并后 /uan/ 韵母下的本韵字 = 十三元.uan ∪ 十四寒.uan ∪ 十五删.uan ∪ ...（去重）
```

### 3. 交互页面生成

两个文件：

**`data.js`**（~1.2 MB）
- 所有数据通过 `JSON.parse` 加载（避免大对象字面量阻塞 JS 引擎）
- 包含 8 个变量：`_RD_CZ`, `_RD_JY`, `_CILIN_CZ`, `_CILIN_JY`, `_SM`, `_CG`, `_CT`, `_CL`

**`index.html`**（~8 KB）
- 纯前端，无服务器依赖
- 双击即可在浏览器运行
- 交互逻辑全在 `<script>` 标签内

---

## 完整复现步骤

### 环境准备

```bash
# 需要 Python 3.8+，推荐安装依赖
pip install pyyaml requests
```

### 步骤 1：下载原始数据

由于原始数据文件较大（超过 50 MB 限制），不直接包含在仓库中。按以下方式获取：

```bash
# 创建原始数据目录
mkdir -p raw

# ── 平水韵 106 韵 ──
# 来源：charlesix59/chinese_word_rhyme（CC-BY）
curl -sL "https://cdn.jsdelivr.net/gh/charlesix59/chinese_word_rhyme@main/data/Pingshui_Rhyme.json" -o raw/Pingshui_Rhyme.json

# ── 词林正韵 19 部 ──
# 来源：charlesix59/chinese_word_rhyme（CC-BY）
curl -sL "https://cdn.jsdelivr.net/gh/charlesix59/chinese_word_rhyme@main/data/Cilin_Rhyme.json" -o raw/Cilin_Rhyme.json

# ── 潮汕音 P0：teochew-lexicon（CC-BY-SA 4.0）──
curl -sL "https://cdn.jsdelivr.net/gh/hokkien-writing/teochew-lexicon@main/character.csv" -o raw/teochew_characters.csv

# ── 潮汕音 P2：kahaani/dieghv 潮州口音（CC-BY-SA 4.0）──
curl -sL "https://raw.githubusercontent.com/kahaani/dieghv/master/dieziu.dict.yaml" -o raw/dieziu.dict.yaml

# ── 潮汕音 P2：kahaani/dieghv 揭阳口音（CC-BY-SA 4.0）──
curl -sL "https://raw.githubusercontent.com/kahaani/dieghv/master/gekion.dict.yaml" -o raw/gekion.dict.yaml

# ── 潮汕音 P1：dieghv 字典（CC-BY-SA 4.0）──
# 不含 entries.yml，需要从 hokkien-writing/dataset 获取
# 或直接使用仓库中的 data/entries_parsed.json（如果已有）
```

### 步骤 2：生成古韵→韵母对照表

```bash
python code/gen_rhyme_by_rhyme.py
```

这个脚本会：
1. 解析平水韵、词林正韵的 JSON 数据
2. 解析潮汕音数据（entries.yml / dieghv 字典）
3. 对每个汉字，按文读优先判韵，判断其潮汕音韵母是否匹配古韵
4. 输出 `data/rhyme_by_rhyme_chaozhou.csv` 和 `rhyme_by_rhyme_jieyang.csv`

### 步骤 3：生成交互式网页

```bash
python code/gen_tool_html.py
```

这个脚本会：
1. 读取 `data/` 下的 CSV 文件
2. 计算词林正韵 19 部的合并数据（按韵母聚合去重）
3. 将所有数据序列化为 JSON，嵌入 `output/data.js`
4. 生成 `output/index.html`（交互页面）

### 步骤 4：使用

用浏览器直接打开 `output/index.html` 即可。

---

## 数据格式说明

### `rhyme_by_rhyme.csv` 格式

| 列 | 说明 | 示例 |
|----|------|------|
| 平水韵韵部 | 韵部名 | 十三元 |
| 声调 | 上平/下平/上声/去声/入声 | 上平 |
| 词林正韵部 | 归属 | 第七部(元寒删先) |
| 潮汕音韵母 | 该韵部中出现的 PUJ 韵母 | uan |
| 此韵母归此韵的字 | 既读此音又在此韵的字 | 繁喧阮原烦源蹯元猿... |
| 同读此韵母但不属此韵的字 | 读此音但不在本韵的字 | 般搬半伴拌柈絆绊... |
| 韵母匹配度 | 本韵字数/总字数 | 32/428 |

### `data.js` 内部数据结构

```javascript
// 平水韵韵部数据（潮州音）
_RD_CZ = {
  "十三元": {
    "uan": { in: ["繁","喧","阮",...], outside: ["般","搬","半",...] },
    "ian": { in: ["阮","原","源",...], outside: ["辦","办","瓣",...] },
    ...
  },
  ...
}

// 词林正韵合并数据（潮州音）
_CILIN_CZ = {
  "第七部": {
    "uan": { in: ["繁","阮","原",...], outside: ["般","搬","川",...] },
    "ian": { in: ["阮","原","源",...], outside: ["辦","编","变",...] },
    ...
  },
  ...
}

// 汉字→韵部映射
_CL = {
  "村": { r: "十三元", s: "上平", c: "第七部" },
  ...
}
```

---

## 后续拓展指南

本项目的架构设计支持多种拓展，以下给出具体指导。

### 1. 拓展口音

当前支持潮州（dieziu）和揭阳（gekion）两种口音。kahaani/dieghv 仓库还包含其他口音的字典文件：

| 口音 | 文件 | 说明 |
|------|------|------|
| 潮州 | `dieziu.dict.yaml` | ✅ 已收录 |
| 揭阳 | `gekion.dict.yaml` | ✅ 已收录 |
| 澄海 | `tenghai.dict.yaml` | 可添加 |
| 饶平 | `riaupeng.dict.yaml` | 可添加 |
| 汕头 | `suantau.dict.yaml` | 可添加 |
| 潮阳 | `dioion.dict.yaml` | 可添加 |

**添加步骤：**

**步骤 A：** 在 `code/gen_rhyme_by_rhyme.py` 中，找到 `parse_rime()` 函数调用处，添加新的口音：

```python
# 在 gen_rhyme_by_rhyme.py 的 main() 函数中
for accent_name, accent_path, label in [
    ('chaozhou', f'{DATA}/dieghv_dieziu.dict.yaml', '潮州音'),
    ('jieyang', f'{DATA}/dieghv_gekion.dict.yaml', '揭阳音'),
    ('tenghai', f'{DATA}/dieghv_tenghai.dict.yaml', '澄海音'),  # 新增
    ('riaupeng', f'{DATA}/dieghv_riaupeng.dict.yaml', '饶平音'),  # 新增
]:
    # ... 处理代码 ...
```

**步骤 B：** 在 `code/gen_tool_html.py` 中，添加新的 JSON.parse 变量和 RD() 切换：

```python
# 在 gen_tool_html.py 中
data_js = '''var _RD_CZ = JSON.parse('...');
var _RD_JY = JSON.parse('...');
var _RD_TH = JSON.parse('...');  # 新增澄海
...
'''
```

**步骤 C：** 在 `index.html` 的 `RD()` 函数和 `showRhyme()` 函数中，增加口音选择分支。

### 2. 多音字文白分层

当前版本对多音字优先取文读（wb=2）。若要更精细处理：

**思路：** 对每个字保存多组数据，分别计算文读版本和白读版本的本韵/别韵。

```python
# 在 gen_rhyme_by_rhyme.py 中，修改 get_fins() 函数
def get_fins(char, accent_dict, layer='literary'):
    if layer == 'literary':
        # 仅用文读
        return wen_fins
    elif layer == 'colloquial':
        # 仅用白读
        return bai_fins
    else:
        # 混合（当前默认）
        return all_fins
```

然后在 `index.html` 界面增加"文读/白读/混合"的下拉选择。

### 3. 拓展古韵（中华新韵等）

**思路：** 当前平水韵 + 词林正韵是固定组合。新增一个古韵体系，需要提供：

1. **该古韵体系的韵部列表**（JSON 格式）
2. **该古韵体系与平水韵的对应关系**（或直接逐字标注）

**具体步骤：**

**步骤 A：** 准备新韵书数据文件（JSON 格式，与 Pingshui_Rhyme.json 一致）：

```json
{
  "上平声部": {
    "一麻": ["啊", "八", "拔", ...],
    "二波": ["波", "播", "博", ...],
    ...
  }
}
```

**步骤 B：** 在 `gen_rhyme_by_rhyme.py` 中添加新的韵书加载逻辑：

```python
# 中华新韵 14 韵
xinyun_rhymes = {
    '一麻': ['啊','八','拔',...],
    '二波': ['波','播','博',...],
    ...
}

NEW_RHYME_TO_PUJ = {
    '一麻': ['a', 'ia', 'ua'],
    '二波': ['o', 'uo'],
    ...
}
```

**步骤 C：** 在 `gen_tool_html.py` 中，添加新的数据变量，并在 `index.html` 的 `index.html` 的模式选择中增加选项。

### 4. 增加韵母映射规则

`PUJ_FINAL_TO_PSY` 映射表在 `gen_rhyme_by_rhyme.py` 中定义。若要修正某个韵母的映射：

```python
PUJ_FINAL_TO_PSY = {
    # 现有规则
    'ong': ['一东','一董','一送','二冬','二肿','二宋'],
    # 新增或修正
    'iong': ['一东','二冬','二肿','二宋','八庚'],  # 如果发现 iong 也对应八庚
}
```

修正后重新运行两个 Python 脚本即可。

### 5. 拓展为可搜索前端

当前是本地 HTML 文件。若要变为在线可访问的页面：

1. 将 `output/` 目录部署到任意静态托管（GitHub Pages、Netlify、Vercel 等）
2. 唯一需要注意的是 `data.js` 约 1.2 MB，确保 CDN 或静态托管能正常提供

---

## 数据来源

| 数据 | 来源 | 直接下载 | 说明 | 许可证 |
|------|------|---------|------|--------|
| 平水韵 106 韵 | [charlesix59/chinese_word_rhyme](https://github.com/charlesix59/chinese_word_rhyme) | [⬇️ Pingshui_Rhyme.json](https://cdn.jsdelivr.net/gh/charlesix59/chinese_word_rhyme@main/data/Pingshui_Rhyme.json) | JSON 格式 | CC-BY |
| 词林正韵 19 部 | [charlesix59/chinese_word_rhyme](https://github.com/charlesix59/chinese_word_rhyme) | [⬇️ Cilin_Rhyme.json](https://cdn.jsdelivr.net/gh/charlesix59/chinese_word_rhyme@main/data/Cilin_Rhyme.json) | JSON 格式 | CC-BY |
| 潮汕音 P0 | [hokkien-writing/teochew-lexicon](https://github.com/hokkien-writing/teochew-lexicon) | [⬇️ character.csv](https://cdn.jsdelivr.net/gh/hokkien-writing/teochew-lexicon@main/character.csv) | CSV，6,169 字 | CC-BY-SA 4.0 |
| 潮汕音 P1 | [hokkien-writing/dataset](https://github.com/hokkien-writing/dataset) | [⬇️ dieghv 字典 (entries.yml)](https://github.com/hokkien-writing/dataset/tree/master/external/dieghv) | YAML，~9,859 字 | CC-BY-SA 4.0 |
| 潮汕音 P2 | [kahaani/dieghv](https://github.com/kahaani/dieghv) | [⬇️ dieziu.dict.yaml (潮州)](https://raw.githubusercontent.com/kahaani/dieghv/master/dieziu.dict.yaml) / [⬇️ gekion.dict.yaml (揭阳)](https://raw.githubusercontent.com/kahaani/dieghv/master/gekion.dict.yaml) | 口音字典，~7,500 字/口音 | CC-BY-SA 4.0 |

### 已尝试但不可用的来源

- **Mogher.com**：潮州音字典 API 已关闭，返回 500
- **搜韵网 (sou-yun.cn)**：潮州音模块已移除，返回 404
- **HuggingFace (Teochew-Wild)**：27 万+字次数据集，网络连接超时

---

## 许可证

本项目代码和整理后的数据以 **CC-BY-SA 4.0** 发布。

仓库 `raw/` 目录已包含全部原始数据。各上游许可证：

- charlesix59/chinese_word_rhyme：CC-BY
- kahaani/dieghv：CC-BY-SA 4.0
- hokkien-writing/teochew-lexicon：CC-BY-SA 4.0

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 数据处理 | Python 3（json, csv, re） |
| 交互页面 | HTML + CSS + JavaScript（纯前端，无框架无依赖） |
| 数据格式 | JSON（通过 JSON.parse 加载） |
| 版控 | Git + GitHub |
