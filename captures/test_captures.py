"""Offline tests: recorded answers of each archive, the network replaced by a table."""
import gzip
import io
import json
import os
import tempfile
import unittest

import captures as C

WAYBACK = json.dumps([
    ["timestamp", "original", "statuscode", "mimetype", "digest", "length"],
    ["20040810120000", "http://perso.example.fr/site/elements.html", "200", "text/html", "AAA", "9000"],
    ["20050101000000", "http://perso.example.fr/site/lost.htm", "200", "text/html", "ERR", "6955"],
    [], ["resume-1"]]).encode()
WAYBACK2 = json.dumps([
    ["timestamp", "original", "statuscode", "mimetype", "digest", "length"],
    ["20060101000000", "http://perso.example.fr/site/other.htm", "200", "text/html", "ERR", "6955"],
    ["20070101000000", "http://perso.example.fr/site/third.htm", "200", "text/html", "ERR", "6955"]]).encode()
ARQUIVO = (b'{"url":"http://perso.example.fr/site/lost.htm","timestamp":"20080101000000","status":"200",'
           b'"mime":"text/html","digest":"BBB","length":"5000"}\n')
CC = (b'{"urlkey":"fr,example,perso)/site/lost.htm","timestamp":"20090101000000","url":"http://perso.example.fr/site/lost.htm",'
      b'"mime":"text/html","status":"200","digest":"CCC","length":"300","offset":"100","filename":"crawl/x.warc.gz"}\n')
TIMEMAP = (b'<http://perso.example.fr/site/lost.htm>; rel="original",\n'
           b'<https://archive.ph/timemap/http://perso.example.fr/site/lost.htm>; rel="self"; type="application/link-format",\n'
           b'<https://archive.ph/20100101000000/http://perso.example.fr/site/lost.htm>; rel="first memento"; '
           b'datetime="Fri, 01 Jan 2010 00:00:00 GMT",\n')
PAGE = b"<html><head><title>Cyliani</title></head><body>" + b"Hermes devoile, texte complet. " * 20 + b"</body></html>"
ERRPAGE = b"<html><head><title>Erreur 404</title></head><body>" + b"x " * 200 + b"</body></html>"


def warc(body: bytes) -> bytes:
    rec = b"WARC/1.0\r\nWARC-Type: response\r\n\r\nHTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + body
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as g:
        g.write(rec)
    return buf.getvalue()


class Net:
    def __init__(self):
        self.calls = []

    def __call__(self, url, headers=None, timeout=90, tries=4):
        self.calls.append(url)
        if "web.archive.org/cdx" in url:
            return 200, (WAYBACK2 if "resumeKey=resume-1" in url else WAYBACK)
        if "arquivo.pt/wayback/cdx" in url:
            return 200, ARQUIVO
        if "collinfo.json" in url:
            return 200, json.dumps([{"id": "CC-MAIN-2009-2010"}, {"id": "CC-MAIN-2024-10"}]).encode()
        if "index.commoncrawl.org/CC-MAIN-2009-2010" in url:
            return 200, CC
        if "data.commoncrawl.org" in url:
            return 206, warc(PAGE)
        if "archive.ph/timemap" in url:
            return 200, TIMEMAP
        if "id_/" in url and "lost.htm" in url:
            return 200, ERRPAGE
        if "id_/" in url:
            return 200, PAGE
        return 404, b""


class T(unittest.TestCase):
    def setUp(self):
        self.net = Net()
        C.get = self.net
        C.time.sleep = lambda s: None

    def test_wayback_resume_key(self):
        rows = C.wayback("perso.example.fr/site/", True, 2004, 2004)
        self.assertEqual(len(rows), 4)
        self.assertTrue(any("resumeKey=resume-1" in u for u in self.net.calls))
        self.assertEqual(rows[0]["replay"], "https://web.archive.org/web/20040810120000id_/http://perso.example.fr/site/elements.html")

    def test_shared_digest_is_error_page(self):
        rows = C.wayback("perso.example.fr/site/", True, 2004, 2004)
        self.assertEqual(C.shared_digests(rows), {"ERR"})

    def test_arquivo_and_cc(self):
        self.assertEqual(C.arquivo("perso.example.fr/site/lost.htm", False, None, None)[0]["digest"], "BBB")
        cc = C.commoncrawl("perso.example.fr/site/lost.htm", False, 2008, 2012)
        self.assertEqual(len(cc), 1)
        self.assertFalse(any("CC-MAIN-2024-10" in u for u in self.net.calls))
        self.assertEqual(C.readable(C.cc_fetch(cc[0]["replay"]))[1], "Cyliani")

    def test_timemap(self):
        rows = C.timemap("archivetoday")("perso.example.fr/site/lost.htm", False, None, None)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ts"], "20100101000000")
        self.assertEqual(rows[0]["url"], "http://perso.example.fr/site/lost.htm")

    def test_variants(self):
        v = C.variants("http://perso.example.fr/site/Le Mercure.htm", ["other.example.fr"])
        for want in ("perso.example.fr/site/Le Mercure.html", "perso.example.fr/site/le mercure.htm",
                     "www.perso.example.fr/site/Le%20Mercure.htm", "other.example.fr/site/Le+Mercure.htm"):
            self.assertIn(want, v)

    def test_readable(self):
        self.assertTrue(C.readable(PAGE)[0])
        self.assertFalse(C.readable(ERRPAGE)[0])
        self.assertFalse(C.readable(b"GIF89a....")[0])

    def test_end_to_end_with_name(self):
        with tempfile.TemporaryDirectory() as d:
            args = C.parser().parse_args(["http://perso.example.fr/site/", "--prefix", "--name", "^lost|^elements",
                                          "--from", "2004", "--to", "2004", "--sources", "wayback", "--fetch", "3", "--out", d])
            res = C.run(args)
            self.assertEqual({r["url"].rsplit("/", 1)[-1] for r in res["captures"]}, {"elements.html", "lost.htm"})
            self.assertEqual([r["url"].rsplit("/", 1)[-1] for r in res["readable"]], ["elements.html"])
            self.assertTrue(os.path.exists(os.path.join(d, res["readable"][0]["file"])))
            md = C.report([res])
            self.assertIn("| wayback | 2 | 2 |", md)
            self.assertIn("Cyliani", md)


if __name__ == "__main__":
    unittest.main()
