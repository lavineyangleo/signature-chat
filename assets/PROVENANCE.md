# 展示素材 / Showcase provenance

- `styles-transparent.png`：本会话真实 C2A 生成的六姓名、三种风格对照图，原始尺寸 1024×1536。
- `bilingual-transparent.png`：本会话真实 C2A 生成的中英文对照图，原始尺寸 1086×1448。
- 两图请求的工具模型均为 `gpt-image-2`；请求字段不构成底层模型身份的独立核验。
- 姓名来自用户明确的开源展示要求：周润发、刘德华、赵丽颖、Lavine、Robert、Alice。中英姓名只作排版对照。
- 原图为白底；本项目 `transparent_signature` 算法提取黑色笔迹形成 RGBA PNG。尺寸保持原样，非透明区域保留真实生成内容。没有伪造性能或生成结果。
- `frontend/public/showcase-transparent.png` 是三风格透明图的副本。
- `frontend/public/examples/*.png` 是上述三风格透明图的真实笔迹裁切，用于首页六个案例；没有重绘或补造签名，仍为透明RGBA图片。
- `logo.svg` 为本项目原创 SVG 字标。
- `demo.gif` 为真实 Vue 页面操作的多帧录制，展示本地样例查看和新建对话；没有进行或伪装实时生图。

The two PNGs derive from actual C2A image-generation outputs requested for open-source display. Black ink was extracted locally into RGBA without changing dimensions. They are original lettering concepts, not authentic celebrity autographs or endorsements. The GIF records real local Vue interactions, not a live generation request.
