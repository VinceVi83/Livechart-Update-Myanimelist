# Livechart-Update-Myanimelist
It export your last completed anime updated from livechart in xml.
You can use this XML generated from script to import to your Myanimelist account.

This script use python3

On Windows :
pip install beautifulsoup4 lxml playwright
py -m playwright install

To use script, it need to get html from www.livechart.me/users/library
How to get it :
On browser, go to www.livechart.me/users/library
Sort by "My Finished Date"
right-click -> inspect element
In tab : Elements to Sources
Save file library in same path as python script

You need to change this value in livechartExportUpdate.py "last = 2 # should be between 1-100"
It will take your xxx last completed anime from page for export.

python livechartExportUpdate.py
On myanimelist, import anime_export.xml to https://myanimelist.net/import.php select MyAnimeListImport

For info, if you want export all your library in livechart contact the support https://www.livechart.me/contact, they can generate for you a XML MAL compatible.
My script is just to update my currect change in list
