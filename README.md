# Reporhogo

One topic, forty-one code forges. Type a word; Reporhogo searches GitHub, GitLab, Codeberg, SourceHut, Gitee, Radicle and thirty-five other forges at once, and lists the repositories in one place.

**Online: https://mauktenieb.github.io/reporhogo/**

A single HTML page. No server, no account, no build step, no dependency: open `index.html` in a browser and it works.

## How it works

- **Live search through public APIs**, from your browser: GitHub, Gitee, Launchpad, Pagure, Radicle (seed.radicle.garden), the Gitea family (Codeberg, Forgejo, Gitea, Gogs, Disroot, NotABug, OpenDev) and the GitLab family (GitLab, Heptapod, GitGud, Framagit).
- **Software Heritage** (archive.softwareheritage.org) fills in every other forge: each archived origin is sorted under its forge by host name.
- **Forges with no public search API** get a direct link to their own search page, or a site-restricted web search.
- Only the forges that hold matching repositories light up. Tap a tile to keep it or leave it out; the results list follows.

## The forty-one forges

Codeberg · Forgejo · Gitea · SourceHut · GitLab · Bitbucket · Gerrit · Phorge · Pagure · Savannah · Launchpad · Fossil · Gogs · OneDev · Radicle · Pijul Nest · GitBucket · Kallithea · Allura · Heptapod · Disroot Git · Tangled · GitGud · repo.or.cz · Gitiles · SourceForge · NotABug · Framagit · Gitee · GitCode · CODING · AtomGit · GitLink · OSDN · OpenDev · GitPrep · Gitblit · Gitweb · Cgit · GitList · GitHub

## Limits

- GitHub allows 10 unauthenticated searches a minute per IP address.
- A forge that is down or blocks cross-origin requests shows in red; the others still answer.

## Contributing

To add a forge: one line in the `F` table of `index.html` (id, name, API family, base URL, search URL, web query, host patterns). Issues and pull requests are welcome.

<!-- network:start -->
## Mauk Tenieb on GitHub

- [mauktenieb.github.io](https://mauktenieb.github.io/): Start here: every site and link.
- [katabase](https://github.com/MaukTenieb/katabase) · [site](https://mauktenieb.github.io/katabase): Korhogo Fauna: concept albums, 18 avatars, lore.
- [insertkoin](https://github.com/MaukTenieb/insertkoin) · [site](https://mauktenieb.github.io/insertkoin/): Insert Koin, the browser arcade: Puck You!, Fauna Chess, Erratik, Faunarratik, Katabatik.
- [3615](https://github.com/MaukTenieb/3615) · [site](https://mauktenieb.github.io/3615/): 3615 KORHOGO, a Minitel terminal in the browser.
- [korhogo](https://github.com/MaukTenieb/korhogo) · [site](https://mauktenieb.github.io/korhogo/): The first Korhogo site.
- [Photofauna](https://github.com/MaukTenieb/Photofauna) · [site](https://mauktenieb.github.io/insertkoin/fotofauna.html): The pocket photo emulator.
- [detour](https://github.com/MaukTenieb/detour): Cuts a sheet of eight portraits into a sprite strip (Python).
- [torview](https://github.com/MaukTenieb/torview) · [site](https://mauktenieb.github.io/torview/): Minimal Tor webview browser (Go).
- [faunator](https://github.com/MaukTenieb/faunator) · [site](https://mauktenieb.github.io/faunator/): Tor inside a web page: web and .onion, no extension (MIT).
- [korhotube](https://github.com/MaukTenieb/korhotube): All the videos of a YouTube channel as JSON: tags, chapters, dubbing, dates (MIT).

Artist: https://github.com/MaukTenieb · Music and sales: https://mauktenieb.bandcamp.com · Journal: https://korhogo.substack.com · Bio: https://orcid.org/0009-0007-9096-8267
<!-- network:end -->

## License

Code: MIT (see `LICENSE`). The names Reporhogo, Korhogo and Korhogo Fauna are not covered by the license.

By [Mauk Tenieb](https://mauktenieb.github.io/). Also part of [Insert Koin](https://mauktenieb.github.io/insertkoin/).
