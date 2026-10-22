#!/usr/bin/env python3
# Runs Reporhogo (index.html of this repository, served locally) in a real Chromium for each topic of
# queue.txt, and writes results.json and results.md: per topic, the forges that answered and the matching
# repositories, sorted by stars. MIT licence (see LICENSE).
import asyncio, json, sys, time
from playwright.async_api import async_playwright

async def main(base, topics):
    out = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p = await b.new_page(viewport={'width': 1280, 'height': 1600})
        await p.goto(base, wait_until='domcontentloaded'); await p.wait_for_timeout(1500)
        for q in topics:
            await p.fill('#q', q); await p.press('#q', 'Enter'); await p.wait_for_timeout(40000)
            st = json.loads(await p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(state).map(([k,v])=>[k,v.s])))'))
            rs = json.loads(await p.evaluate("JSON.stringify(results.filter(rel).map(r=>({forge:r.forge,title:r.title,url:r.url,stars:r.stars||0,desc:(r.desc||'').slice(0,240),date:(r.date||'').slice(0,10)})))"))
            rs.sort(key=lambda r: -(r['stars'] or 0))
            out[q] = {'forges': st, 'results': rs[:100]}
            print(q, len(rs), file=sys.stderr)
        await b.close()
    return out

topics = [l.strip() for l in open(sys.argv[2], encoding='utf-8') if l.strip() and not l.startswith('#')]
R = asyncio.run(main(sys.argv[1], topics))
stamp = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())
json.dump({'checked': stamp, 'topics': R}, open('results.json', 'w'), ensure_ascii=False, indent=1)
with open('results.md', 'w', encoding='utf-8') as f:
    f.write('# Reporhogo — %s\n' % stamp)
    for q, v in R.items():
        lit = [k for k, s in v['forges'].items() if s not in ('err', 'run', 'off')]
        f.write('\n## %s — %d repositories\n\nForges that answered: %s\n\n' % (q, len(v['results']), ', '.join(lit) or 'none'))
        for r in v['results'][:40]:
            f.write('- [%s](%s) — %s · ★ %s · %s · %s\n' % (r['title'], r['url'], r['forge'], r['stars'], r['date'], r['desc'].replace('\n', ' ')))
