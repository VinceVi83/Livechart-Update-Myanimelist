import json
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import sys

BASE_URL = "https://www.livechart.me/anime/"

# pip install beautifulsoup4 lxml playwright
# py -m playwright install
# go to www.livechart.me/users/library
# Sort by "My Modified Date" and display only "Completed" anime
# Ctrl+S to save the file in the script's directory
# python livechartExportUpdate.py or  python livechartExportUpdate.py 15, fetch the last 15 anime
# import anime_export.xml to https://myanimelist.net/import.php select MyAnimeListImport

# ---------------------------
# Anime class
# ---------------------------
class Anime:
    def __init__(self, anime_id, status, episodes_watched=0, rating=0, notes=""):
        self.anime_id = anime_id
        self.status = status.capitalize()
        self.episodes_watched = episodes_watched
        self.rating = rating
        self.notes = notes
        self.name = ""
        self.mal = ""

    def fetch_mal_data(self, page):
        """Visit LiveChart page to fetch the exact title and MyAnimeList link."""
        url = BASE_URL + self.anime_id
        page.goto(url)
        page.wait_for_load_state("networkidle")
        mal_links = page.locator('a[href*="myanimelist.net/anime/"]')
        self.mal = mal_links.first.get_attribute("href") if mal_links.count() else ""
        self.name = page.title().replace(" | LiveChart.me", "")

    def anime_to_xml_element(self):
        """Convert an Anime object into a MyAnimeList-compatible XML element."""
        elem = ET.Element("anime")
        mal_id = self.mal.rstrip("/").split("/")[-1] if self.mal else "0"

        ET.SubElement(elem, "series_animedb_id").text = mal_id
        ET.SubElement(elem, "series_title").text = self.name
        ET.SubElement(elem, "my_status").text = self.status
        ET.SubElement(elem, "my_watched_episodes").text = str(self.episodes_watched)
        ET.SubElement(elem, "my_score").text = str(self.rating)
        ET.SubElement(elem, "my_comments").text = self.notes
        ET.SubElement(elem, "update_on_import").text = "1"
        return elem

    def __repr__(self):
        return (f"Anime(anime={self.name}, id={self.anime_id}, status={self.status.lower()}, "
                f"mal={self.mal}, episodes_watched={self.episodes_watched}, "
                f"rating={self.rating}, notes={self.notes})")

def add_user_info(root, total_anime=3257, watching=9, completed=1469, dropped=17, plantowatch=1731, onhold=31, username="username"):
    """Add user info section to the XML with hardcoded totals."""
    myinfo = ET.SubElement(root, "myinfo")
    ET.SubElement(myinfo, "user_id").text = "0"
    ET.SubElement(myinfo, "user_name").text = username
    ET.SubElement(myinfo, "user_export_type").text = "1"
    ET.SubElement(myinfo, "user_total_anime").text = str(total_anime)
    ET.SubElement(myinfo, "user_total_watching").text = str(watching)
    ET.SubElement(myinfo, "user_total_completed").text = str(completed)
    ET.SubElement(myinfo, "user_total_onhold").text = str(onhold)
    ET.SubElement(myinfo, "user_total_dropped").text = str(dropped)
    ET.SubElement(myinfo, "user_total_plantowatch").text = str(plantowatch)

def export_to_xml(anime_list, filename="anime_export.xml"):
    """Export the anime list to a pretty XML file compatible with MyAnimeList."""
    root = ET.Element("myanimelist")
    for anime in anime_list:
        root.append(anime.anime_to_xml_element())
    add_user_info(root)  # Use hardcoded totals

    # Beautify XML
    rough = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))
    print(f"Exported to {filename}")

# ---------------------------
# Main
# ---------------------------
def main(html_file="My List _ LiveChart.me.html", last=20):
    """Parse the exported HTML file and create MAL-compatible XML."""
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    data = soup.find("div", {"id": "library_entries"})["data-content"]
    parsed = json.loads(data)

    anime_list = []
    for anime_id, info in parsed.items():
        if last and len(anime_list) >= last:
            break
        anime_list.append(Anime(
            anime_id=anime_id,
            status=info.get("status"),
            episodes_watched=info.get("episodes_watched", 0),
            rating=info.get("rating", 0),
            notes=info.get("notes", "")
        ))

    # Launch Playwright to fetch MAL links
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for anime in anime_list:
            anime.fetch_mal_data(page)
            print(anime)
            time.sleep(0.2)  # Short delay to avoid being blocked
        browser.close()

    export_to_xml(anime_list)

if __name__ == "__main__":
    import sys
    last = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(last=last)

