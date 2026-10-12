# 负面词素材库（第 4 步）

每张海报配 20-30 个负面词。不要 10 张复用同一份——不同海报的失败模式不同，针对性负面词能明显提升成品率。

做法是**从下面的通用底座里取 15-20 个，再按该张海报的类型补 5-10 个专项**。

负面词建议以英文为主（主流文生图工具对英文负面词响应更稳），需要时再补中文对照。

## 通用底座（所有海报都适用）

**画质类**
low resolution, low quality, blurry, out of focus, excessive noise, compression artifacts, jpeg artifacts, oversharpened

**结构类**
deformed, distorted, extra limbs, extra fingers, broken limbs, mutated hands, mutated face, disfigured, duplicate subject

**文字类**（电商 KV 的重灾区，每张至少放 4-6 个）
garbled text, misspelled words, wrong characters, gibberish letters, unreadable text, overlapping text, inconsistent font, random Japanese kana, random symbols

**痕迹类**
watermark, signature, artist name, logo of other brands, competitor packaging, trademark text, frame border, vignette artifacts, stains, dust spots

## 按海报类型追加

**海报 01 主 KV**
cluttered background, props stealing focus, product too small, tilted product, wrong packaging color, missing logo, perspective distortion, heavy vignette

**海报 02 生活场景**
irrelevant background, deformed face, unnatural hands, too many objects, messy environment, over-retouched skin, plastic skin texture

**海报 03 工艺 / 概念可视化**
wrong chart type, missing axis labels, misaligned data labels, illogical structure, broken cross-section, overly abstract, unlabeled elements

**海报 04-06 细节特写**
excessive bokeh blurring entire product, blown highlights, wrong material (matte turning metallic), unreadable packaging print, fingerprints, dust

**海报 07 用户评价**
deformed star icons, deformed avatar, wrong quotation marks, text overflowing the card, inconsistent star size

**海报 08 品牌故事 / Moodboard**
off-palette colors, elements with no hierarchy, harsh collage seams, inconsistent color grading

**海报 09 参数表**
misaligned table, broken table lines, garbled numbers, wrong units, Chinese-English misalignment

**海报 10 使用指南**
wrong step numbers, wrong arrow direction, inconsistent icon style, missing safety notice

## 写负面词的三个经验

1. **不是越多越好**。超过 35 个之后模型容易互相牵制，反而削弱正面词。控制在 20-30 个。
2. **别加与正面词冲突的负向**。画面明明要"闪烁的霓虹"，负面词就别写 glowing；要"祖母绿玻璃瓶"，就别写 green。
3. **偏保守比偏激进安全**。宁可少写一个可能有歧义的词，也不要因为一个冲突词搞砸整张图。

## 打包格式

输出时写成一行逗号分隔的英文词组，方便用户直接粘进工具：

```
low resolution, blurry, jpeg artifacts, extra limbs, mutated hands, deformed face, garbled text, misspelled words, unreadable text, inconsistent font, watermark, signature, competitor logo, cluttered background, props stealing focus, product too small, tilted product, wrong packaging color, missing logo, perspective distortion, heavy vignette, dust, fingerprints, over-saturated
```
