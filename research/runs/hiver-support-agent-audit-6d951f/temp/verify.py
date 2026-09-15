import re
t = open('research/notes/final_report_hiver-support-agent-audit-6d951f.md', encoding='utf-8').read()
for pat in [r'A\.2', r'handler A/B', r'5-point', r'5 point', r'500 fresh', r'harness rules', r' [.,;:]', r'  +', r'interim']:
    m = re.findall(pat, t)
    print(pat, '->', len(m), m[:3])
