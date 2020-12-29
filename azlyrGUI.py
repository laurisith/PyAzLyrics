import time
import random
import fnmatch
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import mutagen
from mutagen.id3 import ID3, USLT
from PyAZLyrics import *


class AppGUI:
    def __init__(self, root, last_dir):
        self.root = root
        self.last_dir = last_dir
        root.title("Add Lyrics to MP3")
        root.geometry('%sx%s+0+0' % (self.set_window_size()))
        root.resizable(0, 0)

        lblf_dir = tk.LabelFrame(self.root, text='Select folder with MP3-files' +
                                                ' you want to find and add lyrics:')
        lblf_dir.grid(column=0, row=0, columnspan=2, sticky='we',
                      padx=5, pady=0)

        btn_select_folder = tk.Button(lblf_dir, text='Select Folder',
                                      command=self.select_folder)
        btn_select_folder.grid(column=0, row=0, padx=5, pady=(10, 0), sticky='w')

        self.entry_dir = tk.Entry(lblf_dir, width=64, state='disabled')
        self.entry_dir.grid(column=1, row=0, padx=5, pady=(10, 0), sticky='we')

        scrlbar_dir = tk.Scrollbar(lblf_dir, orient='horizontal',
                                    command=self.entry_dir.xview)
        scrlbar_dir.grid(column=1, row=1, sticky='we')
        self.entry_dir['xscrollcommand'] = scrlbar_dir.set

        lblf_dir_info = tk.LabelFrame(self.root, text='Selected Folder Info:')
        lblf_dir_info.grid(column=0, row=1, columnspan=2, sticky='we',
                           padx=5)

        self.txt_info = tk.Text(lblf_dir_info, width=58, height=10, state='disabled',
                                wrap='word')
        self.txt_info.grid(column=0, row=0)

        scrlbar_info = tk.Scrollbar(lblf_dir_info, orient='vertical',
                                    command=self.txt_info.yview)
        scrlbar_info.grid(column=1, row=0, sticky='ns')
        self.txt_info['yscrollcommand'] = scrlbar_info.set

        self.btn_add_lyrics = tk.Button(self.root, text='Add Lyrics',
                                        state='disabled',
                                        command=self.add_lyrics)
        self.btn_add_lyrics.grid(column=0, row=2, sticky='w', pady=(10, 5),
                                 padx=(5, 0))

        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal',
                                            length=400, mode='determinate')
        self.progress_bar.grid(column=1, row=2, columnspan=1, sticky='we',
                               pady=(10, 5), padx=(0, 5))

    def get_screen_resolution(self):
        """Gets screen resolution."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        return screen_width, screen_height

    def set_window_size(self):
        """Sets GUI-window size depending on screen resolution."""
        if self.get_screen_resolution()[0] < 800:
            gui_width = 500
        else:
            gui_width = 500

        if self.get_screen_resolution()[1] < 600:
            gui_height = 300
        else:
            gui_height = 300
        return gui_width, gui_height

    def progress(self, current_value):
        """ Updates progressbar """
        self.progress_bar['value'] = current_value

    def select_folder(self):
        """Selects folder to work with."""
        sel_folder = filedialog.askdirectory(parent=self.root,
                                             initialdir=self.last_dir)
        if sel_folder == '':
            return
        self.entry_dir['state'] = 'normal'
        self.entry_dir.delete(0, 'end')
        self.entry_dir.insert(0, os.path.abspath(sel_folder))
        self.entry_dir['state'] = 'disabled'
        self.last_dir = sel_folder

        self.folder_info = self.get_dir_info(os.path.abspath(sel_folder))

        self.txt_info['state'] = 'normal'
        self.txt_info.delete('1.0', 'end')
        self.txt_info.insert('1.0', 'MP3 count: ' +
                             str(self.folder_info[0]) + ' files.')
        self.txt_info.insert('end', '\nArtists count: ' +
                             str(len(self.folder_info[1])))
        self.txt_info.insert('end', '\nAlbums count: ' +
                             str(len(self.folder_info[2])))
        self.txt_info.insert('end', '\nRead-only MP3 count: ' +
                             str(self.folder_info[3]))
        self.txt_info.insert('end', '\nArtists found: ' +
                             ', '.join(self.folder_info[1]))

        self.txt_info['state'] = 'disabled'
        if self.folder_info[0] > 0:
            self.btn_add_lyrics['state'] = 'normal'

    def get_dir_info(self, abs_path):
        """Returns info about mp3-files in selected folder and subfolders."""
        mp3_count = 0
        readonly_count = 0
        albums = []
        artists = []
        for r, d, f in os.walk(abs_path):
            mp3_count += len(fnmatch.filter(os.listdir(r), '*.mp3'))

        self.progress_bar['maximum'] = mp3_count
        progress_i = 0

        for r, d, f in os.walk(abs_path):
            for file in f:
                if '.mp3' in file.lower():
                    file_name = os.path.join(r, file)
                    mu_file = mutagen.File(file_name)
                    if not os.access(file_name, os.W_OK):
                        readonly_count += 1
                    try:
                        artist = mu_file['TPE1']
                        if str(artist) not in artists:
                            artists.append(str(artist))
                    except KeyError:
                        pass
                    try:
                        album = mu_file['TALB']
                        if str(album) not in albums:
                            albums.append(str(album))
                    except KeyError:
                        pass
                    progress_i += 1
                    self.progress_bar.after(500, self.progress(progress_i))
                    self.progress_bar.update()

        self.progress_bar.after(500, self.progress(0))
        self.progress_bar.update()

        albums.sort()
        artists.sort()
        return mp3_count, artists, albums, readonly_count

    def add_lyrics(self):
        """Adds lyrics to mp3-files in selected folder and subfolders if
        finds it on azlyrics.com and makes txt-report."""
        start_time = time.clock()
        lyrics_added_count = 0
        sleep_time_total = 0

        with open(os.path.abspath(self.last_dir + '\\report_' +
                                  time.strftime('%Y.%m.%d_%Hh%Mm%Ss',
                                                time.localtime(
                                      time.time())) + '.txt'), 'a') as rep_txt:
            rep_txt.write('\nAdding lyrics was started at ' +
                          str(time.ctime(time.time())) + '\n\n')

            self.progress_bar['maximum'] = self.folder_info[0]
            progress_i = 0

            artists = self.folder_info[1]
            songs_base = {}
            for artist in artists:
                if artists.index(artist) != 0:
                    sleep_time = random.randint(2, 4)
                    time.sleep(sleep_time)
                    sleep_time_total += sleep_time
                    rep_txt.write('Sleep for ' + str(sleep_time) +
                                  ' seconds.\n')
                songs_base[artist] = PyAZLyrics.getAlbums(artist)
            for r, d, f in os.walk(os.path.abspath(self.last_dir)):
                for file in f:
                    if '.mp3' in file.lower():
                        file_name = os.path.join(r, file)
                        rep_txt.write('\nOpen ' + file_name + '\n')
                        if not os.access(file_name, os.W_OK):
                            rep_txt.write('File is READ ONLY!\n')
                        else:

                            mu_file = mutagen.File(file_name)
                            try:
                                artist = str(mu_file['TPE1'])
                            except KeyError:
                                artist = ''
                                rep_txt.write('File has no Artist Tag.\n')
                            try:
                                lyrics = str(mu_file['USLT::eng'])
                            except KeyError:
                                lyrics = 'Empty'
                                rep_txt.write('File has no Lyrics Tag.\n')
                            try:
                                song = str(mu_file['TIT2'])
                            except KeyError:
                                song = ''
                                rep_txt.write('File has no Track Tag.\n')
                            try:
                                number = mu_file['TRCK']
                                try:
                                    number = int(str(number))
                                except ValueError:
                                    slash_index = str(number).find('/')
                                    number = int(str(number)[0:slash_index])
                            except KeyError:
                                number = None
                                rep_txt.write('File has no Track Number Tag.\n')
                            try:
                                album = str(mu_file['TALB'])
                            except KeyError:
                                album = ''
                                rep_txt.write('File has no Album Tag.\n')

                            if artist != '' and song != '':
                                if lyrics_added_count != 0 and \
                                        lyrics_added_count % 6 == 0:
                                    sleep_time = random.randint(3, 6)
                                else:
                                    sleep_time = random.randint(2, 4)
                                time.sleep(sleep_time)
                                sleep_time_total += sleep_time
                                rep_txt.write('Sleep for ' + str(sleep_time) +
                                    ' seconds.\n')

                                az_lyrics = PyAZLyrics.getLyricsMultiSimple(songs_base[artist], song)
                                if az_lyrics == 'NoLyrics' and \
                                    number is not None and album != '':
                                    rep_txt.write('Simple way didn\'t work.\n')
                                    az_lyrics = PyAZLyrics.getLyricsMultiComplex(songs_base[artist], album, song, number)

                                if az_lyrics != 'NoLyrics':
                                    lyrics_added_count += 1
                                    if lyrics == 'Empty':
                                        final_lyrics = artist + ' - ' + song + '\n' + az_lyrics
                                        final_lyrics = final_lyrics.replace('[', '(')
                                        final_lyrics = final_lyrics.replace(']', ')')
                                        mu_file.tags.add(
                                            USLT(encoding=3, lang='eng',
                                                 text=final_lyrics))
                                        mu_file.save()
                                        rep_txt.write(
                                            'Lyrics was added to file.\n')
                                    elif lyrics == '':
                                        final_lyrics = artist + ' - ' + song + '\n' + az_lyrics
                                        final_lyrics = final_lyrics.replace('[', '(')
                                        final_lyrics = final_lyrics.replace(']', ')')
                                        mu_file['USLT::eng'] = USLT(encoding=3,
                                                                    lang='eng',
                                                                    text=final_lyrics)
                                        rep_txt.write(
                                            'Lyrics was added to file.\n')
                                        mu_file.save()
                                    else:
                                        rep_txt.write('File already has some lyrics. New lyrics wasn\'t added to file.\n')
                                else:
                                    rep_txt.write('-'*10 +'! There is no lyrics for song in current syntax of album, song and tracknumber on azlyrics.com. !' +
                                    '-'*10 + '\n')
                            else:
                                rep_txt.write('-'*10 +'! No info in Artist or Song tags. Can\'t search lyrics. !' + '-'*10 + '\n')

                        progress_i += 1
                        self.progress_bar.after(500, self.progress(progress_i))
                        self.progress_bar.update()

            rep_txt.write('\n' + '-'*50 + '\n')
            rep_txt.write('Artists count: ' + str(len(self.folder_info[1])) + '.\n')
            rep_txt.write('MP3 files count: ' + str(self.folder_info[0]) + '.\n')
            rep_txt.write('Lyrics was added to ' + str(lyrics_added_count) +
                          ' files.\n')
            rep_txt.write('Total time: ' + str(int(
                                time.clock()-start_time)) + ' seconds.\n')
            rep_txt.write('Total sleep time: ' + str(sleep_time_total) +
                          ' seconds.\n')
            rep_txt.write('-' * 50)

        messagebox.showinfo('Info',
                            'Lyrics was added in ' + str(int(
                                time.clock()-start_time)) + ' seconds.\n' +
                            'Report file was created in ' + str(self.last_dir) +
                            ' directory.')

        self.progress_bar.after(500, self.progress(0))
        self.progress_bar.update()


def runGUI():
    last_dir = '/'
    master = tk.Tk()
    my_gui = AppGUI(master, last_dir)
    os.chdir(last_dir)
    master.mainloop()


if __name__ == '__main__':
    runGUI()

