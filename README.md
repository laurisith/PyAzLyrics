# PyAzLyrics
python module and GUI for getting lyrics from azlyrics.com

PyAzLyrics module was created for parsing azlyrics.com and getting lyrics from it.
It is based on PyLyrics module (https://pypi.org/project/PyLyrics/).

It contains four functions for this task inside:
1) function of simple lyrics extraction for single artist and song. Use it if you need to get lyrics for one song.
2) function of complex lyrics extraction for single artist and song. Use it if you need to get lyrics for one song
   but info about artist and song returns no lyrics found. This function uses additional conditions based on album name
   and track number.
3) function of simple lyrics extraction for multiple artists and songs. Use it in loops for multiple artists/songs.
4) function of complex lyrics extraction for multiple artists and songs. Use it in loops for multiple artists/songs
   if more conditions like album name and track number are needed.

Module was created to work with Mutagen module (https://pypi.org/project/mutagen/) for getting parameters directly from mp3-files.

The most simple way to start is to run azlyrGUI.py.
Click on Select Folder button to select folder with mp3-files. After folder analysis is done click on Add Lyrics button.
After job is done a report file would be created inside selected folder.
