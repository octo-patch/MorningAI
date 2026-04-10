---
platform: xiaohongshu
style: educational
default_lang: zh
default_items: 5
min_score: 6
image_style: classic
image_lang: zh
---

<!-- 示例模板 — 这是小红书科普体的参考模板。
     创建你自己的风格：
       cp skills/gen-social/templates/xiaohongshu/educational.md skills/gen-social/templates/xiaohongshu/my-style.md
     然后编辑内容。此目录下的自定义模板会被 gitignore。
     在 channel 配置中将 style 设为 "my-style" 即可使用。 -->

## Constraints

- **Title**: ≤ 20 characters, structured and informative
- **Body**: ≤ 1000 characters
- **Tags**: 5-10 hashtags at end of body, format: `#标签`
- **Images**: 3:4 portrait or 1:1 square, carousel supported (3-6 images)
- **Emoji**: Moderate use — structured and clean, not excessive

## Tone & Voice

- Educational, structured, "one article to understand it all"
- Authoritative but approachable
- Use framing like "一文读懂" "看完这篇就够了" "3分钟了解"
- Focus on explaining **why it matters**, not just what happened
- Help readers build knowledge, not just consume headlines

## Content Structure

### Title
- Format: `{emoji} {structured phrase}` (≤ 20 chars)
- Emphasis on comprehensiveness or clarity
- Examples: "📚一文读懂今日AI大事", "🔍AI日报｜5个重要更新", "💡今日AI圈发生了什么"

### Body
1. **Opening** (1 sentence) — context and date
2. **Numbered items** — each with clear structure:
   - `{number}️⃣ {Entity} — {Event}`
   - **What**: 1 sentence on what happened
   - **Why it matters**: 1 sentence on significance
   - **Key metric** (if available): number or comparison
3. **Summary takeaway** — "今日关键词：..." or trend observation
4. **Tags** — 5-10 relevant hashtags

### Body Format Rules
- Numbered list (1️⃣ 2️⃣ 3️⃣ etc.)
- Clear separation between "what" and "why"
- Bold key terms with 【】brackets
- Use ▸ or → for sub-points
- Line breaks between each numbered item

## Character Limit Rules

| Component | Budget |
|-----------|--------|
| Title | ≤ 20 chars |
| Opening | ~30-50 chars |
| Per item block | ~100-180 chars |
| Summary takeaway | ~50-80 chars |
| Tags | ~100-150 chars |
| **Total body** | **≤ 1000 chars** |

## Output Format

```
---xiaohongshu---

---title---
{emoji} {title text}

---body---
{structured body with numbered items}

#tag1 #tag2 #tag3 #tag4 #tag5

---images---
1: {image_filename}
2: {image_filename}
3: {image_filename}
4: {image_filename}
```

## Example Output

```
---xiaohongshu---

---title---
📚一文读懂今日AI大事

---body---
4月8日AI圈5个重要更新，看完这篇就够了👇

1️⃣ Anthropic — Claude 4.5 Sonnet 发布
▸ 新一代中端模型，编程能力提升18%
▸ 上下文扩展到200K，速度提升40%
→ 意味着：日常AI编程助手体验将大幅升级

2️⃣ Google — Gemini 2.5 Flash 公测
▸ 100万上下文窗口，支持多模态推理
▸ AI Studio免费用，Vertex AI付费版
→ 意味着：长文档处理能力进入新阶段

3️⃣ DeepSeek — V3-0407 开源
▸ 671B参数MoE架构，MIT协议
▸ 性能接近GPT-4o，成本极低
→ 意味着：开源模型正式追平闭源前沿

4️⃣ Cursor — 后台Agent正式上线
▸ 无需盯屏幕，后台自动重构和提PR
▸ Pro版最多10个Agent并发
→ 意味着：编程工作流正在走向全自动

5️⃣ Windsurf — 2亿美元C轮融资
▸ 估值30亿美元，Insight Partners领投
→ 意味着：AI编程工具赛道资本持续加注

📌 今日关键词：模型升级、开源突破、编程自动化

#AI日报 #人工智能 #Claude #Gemini #DeepSeek #Cursor #AI科普 #科技圈 #大模型

---images---
1: social_2026-04-08_xhs_kepu_zh_1.png
2: social_2026-04-08_xhs_kepu_zh_2.png
3: social_2026-04-08_xhs_kepu_zh_3.png
4: social_2026-04-08_xhs_kepu_zh_4.png
```
