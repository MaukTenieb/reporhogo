# Reporhogo

By Mauk Tenieb & Korhogo. Build guide: [MaukTenieb/method](https://github.com/MaukTenieb/method).

Reporhogo searches forty-one code forges for a topic and lists the repositories it finds. Type a word. Reporhogo searches GitHub, GitLab, Codeberg, SourceHut, Gitee, Radicle and 35 other forges at once, and lists the repositories in one place.

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
