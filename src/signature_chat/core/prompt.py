from signature_chat.core.styles import design_policy


def build_prompt(messages: list[str]) -> str:
    if not messages or len(messages) > 50:
        raise ValueError('对话应包含1至50条要求，请开始新对话。')
    if any(not isinstance(m, str) or not m.strip() or len(m) > 2000 for m in messages):
        raise ValueError('每条要求应为1至2000字。')
    context = '\n\n'.join(f'User request {i + 1}: {text}' for i, text in enumerate(messages))
    if len(context) > 20000:
        raise ValueError('对话已过长，请开始新对话。')
    policy = design_policy(messages)
    color_rule = ('BLACK INK CONTOURS with restrained pastel accent fills inside the illustration. Preserve the chosen accent colors; keep all surrounding canvas transparent.'
                  if policy['preserve_color'] else 'BLACK INK ONLY. No color fills.')
    return '\n'.join([
        'Design original handwritten signature lettering using the conversation below. Latest user instructions take precedence.',
        'Use the exact provided names, character order and capitalization. Do not invent translations or copy authentic celebrity autographs.',
        color_rule,
        'Transparent background. If transparency is unavailable, use absolute pure white. No textures, shadows, opaque panels or checkerboard pixels.',
        'Default aesthetic: fine fountain-pen strokes, natural pressure variation, connected cursive, airy horizontal composition, graceful elliptical loops and long terminal hairlines.',
        ('Create one integrated illustrated signature, not a three-style specimen sheet. ' + policy['guidance']
         if policy['illustrated'] else 'Default comparison: three clearly different styles (legible restrained everyday handwriting; expansive oval-loop ornamental cursive; sharp compressed forward-slanted fast autograph). Use one style if the user asks for one.'),
        'Chinese uses genuine running-script stroke structures; English stays readable. Only use the languages and names actually provided. A new name replaces earlier names unless comparison is requested.',
        ('Show the name woven into the requested motif; no extra captions or typeset name labels. Motifs share strokes with lettering. Keep the name readable and use an original character design.'
         if policy['illustrated'] else 'Show signatures and small name labels only, with generous spacing.'),
        'No conversation text, UI, borders or watermarks. This is text-guided regeneration, not pixel editing of a previous image.',
        context,
    ])
