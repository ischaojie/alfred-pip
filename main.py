import argparse
import sys

from bs4 import BeautifulSoup
from workflow import Workflow3, web

PYPI_URL = "https://pypi.org"

wf = Workflow3(libraries=["./libs"])
logger = wf.logger


def search_packages(query):
    url = f"{PYPI_URL}/search/"
    params = {"q": query}
    r = web.get(url, params=params)
    assert r.status_code == 200
    soup = BeautifulSoup(r.text, "html.parser")
    pkgs = []
    for pkg in soup.find_all("a", class_="package-snippet"):
        url = PYPI_URL + pkg.get("href")
        info = [span.get_text() for span in pkg.h3.children]
        info = [i.replace("\n", "") for i in info if i != "\n"]
        name, version, created = info
        desc = pkg.p.get_text()

        pkgs.append(
            dict(
                name=name,
                version=version,
                created=created,
                desc=desc,
                url=url,
            )
        )
    return pkgs


def app(wf: Workflow3):
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", nargs="?", default=False)
    parser.add_argument("query", nargs="?", default=None)
    args = parser.parse_args(wf.args)
    query = args.query
    if not query:
        return
    pkgs = search_packages(query)
    for pkg in pkgs:
        wf.add_item(
            title="{} {}".format(pkg["name"], pkg["version"]),
            subtitle=pkg["desc"],
            arg=pkg["url"],
            icon="icons/cubes.svg",
            valid=True,
        )

    wf.send_feedback()


if __name__ == "__main__":
    sys.exit(wf.run(app))
