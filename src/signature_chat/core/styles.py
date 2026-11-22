import re

ILLUSTRATED_STYLES = {
    '萌宠线描': 'Original minimalist cute animal line-art signature. Integrate ears, head, paws or tail into the initial, connecting stroke or ending. Rounded clean black monoline, tiny friendly face, readable cursive name. Use the requested animal; if unspecified use a small original kitten.',
    '花植点缀': 'Original botanical signature. Grow a simple rose, small flower, leaf or butterfly from a name stroke. Fine black ink, airy spacing, restrained petals, light organic flow. Share strokes between lettering and motif rather than attaching unrelated clipart.',
    '星月童话': 'Original celestial doodle signature. Integrate a crescent moon, tiny four-point star, shell or teacup into the initial or finishing stroke. Use only one main motif and two or three small sparkles. Minimal rounded black line art and readable handwritten name.',
    '淡彩萌系': 'Original pastel illustrated signature. Black rounded ink contours with a small animal or botanical motif woven into the name. Add only small blush pink, peach, warm cream or light brown accent fills inside the motif. No colored background, gradients, realistic shading or large color blocks.',
}
PLAIN_STYLES = {
    '简洁易读': 'Create one signature only. Legible restrained everyday handwriting, minimal decoration, clear open spacing.',
    '回环花式': 'Create one signature only. Expansive oval loops, flowing connected cursive and long fine terminal strokes.',
    '利落速签': 'Create one signature only. Compact forward-slanted handwriting, decisive angular turns and a straight finishing stroke.',
    '三款对照': 'Create three clearly different signatures of the same name: legible restrained everyday handwriting; expansive oval-loop ornamental cursive; sharp compressed forward-slanted fast autograph.',
}


def design_policy(messages):
    """Resolve explicit style markers and later color changes in conversation order."""
    style = None
    color = False
    names = '|'.join((*ILLUSTRATED_STYLES, *PLAIN_STYLES))
    for text in messages:
        markers = re.findall(r'【(?:风格：)?([^】]+)】', text)
        source = markers[-1] if markers else text
        matches = re.findall(names, source)
        if '同一姓名分别生成' in source:
            style, color = '三款对照', False
        elif matches:
            style = matches[-1]
            color = style == '淡彩萌系'
        if re.search(r'淡彩|彩色|粉色|奶黄|浅棕|pastel|color accents', text, re.I):
            color = True
        if re.search(r'黑白|纯黑|去掉颜色|不要(?:颜色|彩色|淡彩)|black[- ]and[- ]white|monochrome', text, re.I):
            color = False
    return {'style': style, 'illustrated': style in ILLUSTRATED_STYLES,
            'preserve_color': color, 'guidance': ILLUSTRATED_STYLES.get(style, PLAIN_STYLES.get(style, ''))}
