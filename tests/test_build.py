import copy
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import build


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class StaticSiteTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(build.DATA.read_text(encoding="utf-8"))

    def test_catalog_is_readable_without_javascript(self):
        doc = Document(build.render_site(self.data))
        cards = [
            attrs
            for tag, attrs in doc.elements
            if tag == "article" and attrs.get("class") == "card"
        ]
        entries = [e for section in self.data["sections"] for e in section["entries"]]
        self.assertEqual(len(cards), len(entries))
        self.assertTrue(all("hidden" not in card for card in cards))
        text = "".join(doc.text)
        links = {attrs.get("href") for tag, attrs in doc.elements if tag == "a"}
        descriptions = {
            attrs.get("title")
            for tag, attrs in doc.elements
            if attrs.get("class") == "desc"
        }
        for entry in entries:
            self.assertIn(entry["name"], text)
            self.assertIn(entry["url"], links)
            if entry.get("desc"):
                self.assertIn(entry["desc"], descriptions)
            for tag in entry.get("tags", []):
                self.assertIn("#" + tag, text)
        for entry in self.data["archived"]:
            self.assertIn(entry["name"], text)
            for link in entry.get("links", []):
                self.assertIn(link["url"], links)
        self.assertIn(
            ("link", {"rel": "canonical", "href": build.SITE_URL}), doc.elements
        )
        self.assertTrue(
            any(a.get("name") == "google-site-verification" for _, a in doc.elements)
        )
        scripts = [a for t, a in doc.elements if t == "script"]
        self.assertEqual(scripts, [{"src": "assets/shelf.js", "defer": None}])
        for tag, attrs in doc.elements:
            if tag == "img":
                self.assertNotIn("src", attrs)
                self.assertTrue(attrs["data-src"].startswith("https://"))

    def test_text_and_attributes_are_escaped_and_description_links_survive(self):
        data = copy.deepcopy(self.data)
        entry = data["sections"][0]["entries"][0]
        entry.update(
            name="test/<script>alert(1)</script>",
            desc='"<& [reference](https://example.com/?a=1&b=2)',
            tags=['" onclick="alert(1)'],
        )
        doc = Document(build.render_site(data))
        self.assertEqual(sum(tag == "script" for tag, _ in doc.elements), 1)
        self.assertFalse(
            any(key.startswith("on") for _, attrs in doc.elements for key in attrs)
        )
        self.assertIn(
            (
                "a",
                {
                    "href": "https://example.com/?a=1&b=2",
                    "target": "_blank",
                    "rel": "noopener",
                },
            ),
            doc.elements,
        )
        self.assertIn(entry["name"], "".join(doc.text))

    def test_executable_urls_and_invalid_section_keys_fail_build(self):
        for url in [
            "javascript:alert(1)",
            "data:text/html,test",
            "//example.com",
            "https://example.com/\n",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                build.safe_url(url)
        self.data["sections"][0]["key"] = 'bad" onclick="x'
        with self.assertRaises(ValueError):
            build.render_site(self.data)

    def test_build_updates_html_from_json_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path, readme, index = (
                root / name for name in ["shelf.json", "README.md", "index.html"]
            )
            self.data["sections"][0]["entries"].append(
                {
                    "name": "Fresh catalog item",
                    "url": "https://example.com/new",
                    "desc": "New description",
                    "tags": ["new-tag"],
                }
            )
            data_path.write_text(json.dumps(self.data), encoding="utf-8")
            with patch.multiple(build, DATA=data_path, README=readme, INDEX=index):
                self.assertEqual(build.main(), 0)
                first = index.read_bytes()
                self.assertIn(b"Fresh catalog item", first)
                self.assertIn("Fresh catalog item", readme.read_text())
                self.assertEqual(build.main(), 0)
                self.assertEqual(first, index.read_bytes())


if __name__ == "__main__":
    unittest.main()
