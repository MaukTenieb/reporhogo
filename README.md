# Reporhogo

By Mauk Tenieb & Korhogo. Build guide: [MaukTenieb/method](https://github.com/MaukTenieb/method).

Reporhogo searches forty-one code forges for a topic and lists the repositories it finds. Its tool Captures searches eight web archives for a lost page. Type a word. Reporhogo searches GitHub, GitLab, Codeberg, SourceHut, Gitee, Radicle and 35 other forges at once, and lists the repositories in one place.

Online: https://mauktenieb.github.io/reporhogo/

Reporhogo is one HTML file; a browser opens `index.html` and runs the search directly.

## How it works

- Your browser searches live through public APIs: GitHub, Gitee, Launchpad, Pagure, Radicle (seed.radicle.garden), the Gitea family (Codeberg, Forgejo, Gitea, Gogs, Disroot, NotABug, OpenDev) and the GitLab family (GitLab, Heptapod, GitGud, Framagit).
- Software Heritage (archive.softwareheritage.org) fills in every other forge. Reporhogo sorts each archived origin under its forge by host name.
- For forges that offer a web search page only, Reporhogo gives a direct link to that page, or a site-restricted web search.
- The tiles of the forges with matching repositories light up. Tap a tile to keep it or leave it out; the results list follows.

## The forty-one forges

Codeberg · Forgejo · Gitea · SourceHut · GitLab · Bitbucket · Gerrit · Phorge · Pagure · Savannah · Launchpad · Fossil · Gogs · OneDev · Radicle · Pijul Nest · GitBucket · Kallithea · Allura · Heptapod · Disroot Git · Tangled · GitGud · repo.or.cz · Gitiles · SourceForge · NotABug · Framagit · Gitee · GitCode · CODING · AtomGit · GitLink · OSDN · OpenDev · GitPrep · Gitblit · Gitweb · Cgit · GitList · GitHub

## Search from a file

Write topics in `queue.txt`, one per line, and push it to `main`. GitHub Actions then runs Reporhogo in a real browser on each topic and writes the results to the branch `result`. `results.md` lists, per topic, the forges that answered and the matching repositories, sorted by stars; `results.json` gives the same data as JSON.

## Web archives

`captures/captures.py` lists every capture of a web address, or of a whole site, in eight public web archives, then downloads the captures that hold a readable page.

| id | archive | reach |
|---|---|---|
| `wayback` | Internet Archive, Wayback Machine | address or whole site, year by year |
| `arquivo` | Arquivo.pt | address or whole site, year by year |
| `commoncrawl` | Common Crawl, every crawl since 2008 | address or whole site, crawl by crawl |
| `archivetoday` | archive.today (archive.ph) | address |
| `loc` | Library of Congress | address |
| `ukwa` | UK Web Archive | address |
| `memento` | Memento Time Travel: national and university archives in one query | address |
| `ghost` | Ghost Archive | address |

- Every capture counts: the indexes run with `collapse` off, page by page (`resumeKey`), one year or one crawl at a time.
- An old host often answers a dead page with its error page and the code 200, and the archives keep that error page as a valid capture. One digest under three addresses or more marks it; the download skips it.
- `--prefix` lists every address ever captured under a site, including file names absent from any link; `--name` keeps the file names that match a pattern.
- One address goes out under its spellings: `http` and `https`, bare host and `www`, `.htm` and `.html`, lower case, spaces as `%20`, `+` and `_`, other hosts of the same site (`--alias`).
- `--fetch N` downloads up to N captures with distinct content per address and keeps the first readable page. Common Crawl pages come out of their WARC file by byte range.

```bash
cd captures
python3 captures.py http://example.fr/page.htm --alias www2.example.fr --fetch 5
python3 captures.py http://example.fr/ --prefix --name "^(page|other)\.html?$" --from 2001 --to 2012 --fetch 5
```

Python 3.9 or later, standard library only. From a file: one search per line in `captures/queue.txt`; in the tab Actions, "Search the web archives", then "Run workflow". The results go to the branch `archives`: `results.md`, `results.json`, `pages/`. archive.today shows a CAPTCHA to scripts; Captures then gives its address for a browser. Tests: `python3 -m unittest test_captures`, offline.

## Limits

- GitHub allows 10 unauthenticated searches a minute per IP address.
- A forge that is down or blocks cross-origin requests shows in red; the others still answer.

## Contributing

To add a forge, add one line to the `F` table of `index.html` (id, name, API family, base URL, search URL, web query, host patterns). Issues and pull requests are welcome.

<!-- network:start -->
## Provenance

Built for [Insert Koin](https://mauktenieb.github.io/insertkoin/), Mauk Tenieb's Korhogo world, games and machines in a browser, where it has its own room.

Other tools by Mauk Tenieb: [Detour](https://github.com/MaukTenieb/detour): cuts portrait sheets into sprite strips and places the eye lights · [FaunaTor](https://github.com/MaukTenieb/faunator): reads web and .onion pages through Tor clients that run in the page · [KorhoTube](https://github.com/MaukTenieb/korhotube): lists the public videos of a YouTube channel as JSON · [Photofauna](https://github.com/MaukTenieb/Photofauna): a photo editor with 44 looks, part of Insert Koin · [TorView](https://github.com/MaukTenieb/torview): a desktop browser in Go that routes its traffic through the official Tor daemon.

Index of Mauk Tenieb's sites: https://mauktenieb.github.io/
<!-- network:end -->

Related: [mauktenieb.github.io](https://mauktenieb.github.io/) · [MaukTenieb/method](https://github.com/MaukTenieb/method)

## Rights

Code under MIT, method under CC BY 4.0, Korhogo material reserved; credit Mauk Tenieb & Korhogo. Details: [LICENSE](LICENSE).
