import re
t = open('research/notes/final_report_hiver-support-agent-audit-6d951f.md', encoding='utf-8').read()
print('cites:', len(re.findall(r'\[\[[a-z0-9][a-z0-9-]*\]\]', t)))
print('badcite:', len(re.findall(r'\[\[[^\]]* [^\]]*\]\]', t)))
print('interim:', len(re.findall(r'interim', t)))
print('h2:', len(re.findall(r'^## \d+\.', t, flags=re.M)))
print('dblspace:', len(re.findall(r'  +', t)))
print('words:', len(t.split()))
