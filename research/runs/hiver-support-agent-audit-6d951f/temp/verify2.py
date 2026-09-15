import re
t = open('research/notes/final_report_hiver-support-agent-audit-6d951f.md', encoding='utf-8').read()
for m in list(re.finditer(r'A\.2', t))[:2] + list(re.finditer(r'5-point', t))[:2]:
    s = max(0, m.start() - 400)
    seg = t[s:m.end() + 200]
    cites = re.findall(r'\[\[[a-z0-9][a-z0-9-]*\]\]', seg)
    print('---', m.group(), '| nearby cites:', cites[:6])
