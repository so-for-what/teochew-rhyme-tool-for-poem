# 数据来源与许可证声明

本仓库包含两类数据：

- **原始数据**（`raw/`）：从上游项目直接下载，未经修改
- **处理数据**（`raw/entries_parsed.json`）：从上游数据解析转换而来

## 原始数据

| 文件 | 来源 | 许可证 |
|------|------|--------|
| `Pingshui_Rhyme.json` | [charlesix59/chinese_word_rhyme](https://github.com/charlesix59/chinese_word_rhyme) | CC-BY |
| `Cilin_Rhyme.json` | [charlesix59/chinese_word_rhyme](https://github.com/charlesix59/chinese_word_rhyme) | CC-BY |
| `character.csv` | [hokkien-writing/teochew-lexicon](https://github.com/hokkien-writing/teochew-lexicon) | CC-BY-SA 4.0 |
| `dieziu.dict.yaml` | [kahaani/dieghv](https://github.com/kahaani/dieghv) | CC-BY-SA 4.0 |
| `gekion.dict.yaml` | [kahaani/dieghv](https://github.com/kahaani/dieghv) | CC-BY-SA 4.0 |

## 处理数据

| 文件 | 来源 | 处理方式 |
|------|------|---------|
| `entries_parsed.json` | 从 [hokkien-writing/dataset](https://github.com/hokkien-writing/dataset/tree/master/external/dieghv) 的 `entries.yml` 解析 | 提取 PUJ 读音字段，保留文读(wb=2)/白读(wb=1)标记 |

## 致谢

感谢以下开源项目的贡献：

- [charlesix59/chinese_word_rhyme](https://github.com/charlesix59/chinese_word_rhyme) — 平水韵与词林正韵逐字数据库
- [kahaani/dieghv](https://github.com/kahaani/dieghv) — 潮汕话 PUJ 拼音字典
- [hokkien-writing/teochew-lexicon](https://github.com/hokkien-writing/teochew-lexicon) — 潮州话逐字词数据库
- [hokkien-writing/dataset](https://github.com/hokkien-writing/dataset) — dieghv 字典排版整理版

## 许可证

- 本仓库代码和整理后的数据：**CC-BY-SA 4.0**
- 各上游数据保持其原始许可证

使用时请保留上游署名。若有任何不妥，请提 issue 告知。

---

*本项目为学术交流目的构建，不涉及商业用途。*