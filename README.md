# Reporhogo

Reporhogo searches forty-one code forges for a topic and lists the repositories it finds. Type a word; Reporhogo searches GitHub, GitLab, Codeberg, SourceHut, Gitee, Radicle and thirty-five other forges at once, and lists the repositories in one place.

**Online: https://mauktenieb.github.io/reporhogo/**

Reporhogo is one HTML file; a browser opens `index.html` and runs the search directly.

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
## Provenance

Built for [Insert Koin](https://mauktenieb.github.io/insertkoin/), Mauk Tenieb's browser games set in Korhogo, where it has its own room.

Other tools by Mauk Tenieb: [Detour](https://github.com/MaukTenieb/detour): cuts portrait sheets into sprite strips and places the eye lights · [FaunaTor](https://github.com/MaukTenieb/faunator): reads web and .onion pages through Tor clients that run in the page · [KorhoTube](https://github.com/MaukTenieb/korhotube): lists every video of a YouTube channel as JSON · [Photofauna](https://github.com/MaukTenieb/Photofauna): a photo editor with 44 looks, part of Insert Koin · [TorView](https://github.com/MaukTenieb/torview): a desktop browser in Go that routes its traffic through the official Tor daemon.

Index of Mauk Tenieb's sites: https://mauktenieb.github.io/
<!-- network:end -->

## License

Code: MIT (see `LICENSE`). The names Reporhogo, Korhogo and Korhogo Fauna are not covered by the license.

By [Mauk Tenieb](https://mauktenieb.github.io/). Also part of [Insert Koin](https://mauktenieb.github.io/insertkoin/).
