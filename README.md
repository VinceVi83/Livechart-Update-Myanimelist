# Livechart-Update-Myanimelist
It export your last completed anime updated from Livechart in xml.<br>
You can use this XML generated from script to import to your Myanimelist account.<br>

For info, if you want export all your library from Livechart, contact the support https://www.livechart.me/contact, they can generate for you a XML MAL compatible.<br>
My script is just to update my current change in Livechart to MAL.

This script use python3<br>

On Windows :<br>
pip install beautifulsoup4 lxml playwright<br>
py -m playwright install<br>

To use script, you need to get html from www.livechart.me/users/library<br>
How to get it :<br>
On browser, go to www.livechart.me/users/library<br>
Sort by "My Finished Date"<br>
right-click -> inspect element<br>
In tab : Elements to Sources<br>
Save file library in same path as python script<br>

You need to change this value in livechartExportUpdate.py "last = 2 # should be between 1-100"<br>
It will take your xxx last completed anime from page for export.

python livechartExportUpdate.py<br>
On myanimelist, import anime_export.xml to https://myanimelist.net/import.php select MyAnimeListImport
