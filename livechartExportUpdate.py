import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET
from xml.dom import minidom

# pip install beautifulsoup4 lxml playwright
# py -m playwright install

# go to www.livechart.me/users/library
# Sort by "My Finished Date"
# right-click -> inspect element
# In tab Elements to Sources
# Save file library in same path as python script
# python livechartExportUpdate.py
# import anime_export.xml to https://myanimelist.net/import.php select MyAnimeListImport

last = 2 # should be between 1-100
baseUrl = "https://www.livechart.me"
filename = "library"  # HTML file saved from your /library page

def extract_mal_id(mal_url):
    # Extract numeric ID from MAL URL
    try:
        return mal_url.rstrip('/').split('/')[-1]
    except Exception:
        return "0"
        
def anime_to_xml_element(anime):
    anime_elem = ET.Element("anime")

    mal_id = extract_mal_id(anime.mal)
    title = anime.name
    status = "Completed" if anime.episode_progress.isdigit() else "Plan to Watch"
    watched_episodes = anime.episode_progress if anime.episode_progress.isdigit() else "0"

    ET.SubElement(anime_elem, "series_animedb_id").text = mal_id

    title_elem = ET.SubElement(anime_elem, "series_title")
    title_elem.text = None
    title_elem.append(ET.Comment(f"[CDATA[{title}]]"))

    ET.SubElement(anime_elem, "my_status").text = status
    ET.SubElement(anime_elem, "my_watched_episodes").text = watched_episodes
    ET.SubElement(anime_elem, "update_on_import").text = "1"

    return anime_elem

def add_myinfo_element(root, total, watching, completed, dropped, plantowatch, onhold):
    # Add a myinfo element to XML to satisfy MAL import requirements
    myinfo = ET.SubElement(root, "myinfo")
    ET.SubElement(myinfo, "user_id").text = "0"
    ET.SubElement(myinfo, "user_name").text = "username"
    ET.SubElement(myinfo, "user_export_type").text = "1"
    ET.SubElement(myinfo, "user_total_anime").text = str(total)
    ET.SubElement(myinfo, "user_total_watching").text = str(watching)
    ET.SubElement(myinfo, "user_total_completed").text = str(completed)
    ET.SubElement(myinfo, "user_total_onhold").text = str(onhold)
    ET.SubElement(myinfo, "user_total_dropped").text = str(dropped)
    ET.SubElement(myinfo, "user_total_plantowatch").text = str(plantowatch)

def export_anime_list_to_xml(animeList, filename="anime_export.xml"):
    root = ET.Element("myanimelist")
    
    count = 0
    for anime in animeList:
        root.append(anime_to_xml_element(anime))
        count = count + 1
        if count >= last:
            break
    
    # Fake data (no effect on your own list)
    total_anime = 3257
    total_completed = 1469
    total_watching = 9
    total_dropped = 17
    total_plantowatch = 1731
    total_onhold = 31

    add_myinfo_element(root,
                      total_anime,
                      total_watching,
                      total_completed,
                      total_dropped,
                      total_plantowatch,
                      total_onhold)

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Write XML to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

class Anime:
    def __init__(self, name, live):
        self.name = name
        self.live = live
        self.episode_progress = "N/A"
        self.mal = ""

    def getMalLink(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = baseUrl + self.live
            page.goto(url)
            print(f"🔍 Fetching MAL link for: {self.name}")
            page.wait_for_load_state("networkidle")
            mal_links = page.locator('a[href*="myanimelist.net/anime/"]')
            if mal_links.count() > 0:
                self.mal = mal_links.first.get_attribute("href")
            else:
                self.mal = "Not found"
            browser.close()

    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"Livechart URL: {baseUrl + self.live}\n"
            f"Episode Progress: {self.episode_progress}\n"
            f"MyAnimeList URL: {self.mal}\n"
        )

animeList = []

# Parse local HTML file
with open(filename, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")
    elements = soup.select(".link.link-hover.font-medium")
    # Extract href and title for each element
    for i, el in enumerate(elements, 1):
        href = el.get("href", "")
        title = el.get("title", "")
        tmp = Anime(title, href)
        animeList.append(tmp)

    # Find all span tags with attribute data-user-library-anime-target="episodeProgress"
    spans = soup.find_all('span', {'data-user-library-anime-target': 'episodeProgress'})

    # Collect all episode progress texts in a list
    progress_values = [span.text for span in spans]
    print(f"Found episode progress values count: {len(progress_values)}")
    for index in range(len(progress_values)):
        animeList[index].episode_progress = progress_values[index]

# Fetch MyAnimeList links (limited to "last updated" to avoid too many requests)
for i, anime in enumerate(animeList[:last]):
    anime.getMalLink()
    time.sleep(1)  # avoid spamming the site

export_anime_list_to_xml(animeList)
