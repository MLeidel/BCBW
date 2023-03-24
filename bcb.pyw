'''
bcb.py
Windows version of descq
Uses tkinter instead of Gtk
July 2021
'''
import webbrowser
import requests
import subprocess
import os
from tkinter import *
from tkinter.ttk import *  # defaults all widgets as ttk
from ttkthemes import ThemedTk  # module applied to all widgets
from time import strftime
import requests
from urllib.parse import quote

# ############ GUI COLORS
g_e_font = "Consolas 10 bold"  # Entry font
# ############ GLOBALS
b_deco = False  # global for captions (use cap and winset to change)
b_topm = True   # global for z-order (use top and winset to change)
leng = 25       # default length of entry
MAXHIST = 10    # entry history limit (ehist.txt)
t = None        # global for toplevel windows
# maxurls = 100 l # set a limit for too many URLS
# ############


class Application(Frame):
    '''
    This application has a very small GUI
    consisting of a grid layout with one entry widget.
    Some functionality is performed with secondary
    "Toplevel" windows
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=0, pady=0)
        self.last_command = ""
        self.create_widgets()
        self.entry1.focus()

    def create_widgets(self):
        ''' ENTIRE INTERFACE IS ONE ENTRY FIELD '''
        global leng

        self.inx = MAXHIST
        self.hislst = []

        self.entry1 = Entry(self, font=g_e_font)
        self.entry1.grid(row=1, column=1, padx=(6, 3))
        self.entry1.bind('<Return>', self.process_events)
        self.entry1.bind('<Tab>', self.process_events)
        # blank the entry box with Esc key
        self.entry1.bind('<Escape>', self.clear_entry)
        self.entry1.configure(width=leng)
        self.entry1.bind("<Up>", self.up_arrow)
        self.entry1.bind("<Down>", self.down_arrow)

        self.btnsave = Button(self, text='■', command=self.saveFromClip,
                              width=2)
        self.btnsave.grid(row=1, column=2, padx=(3, 6), pady=2)

        with open("edit.txt", "r", encoding='utf-8') as f_hand:
            self.editor = f_hand.readline().strip()

        with open("seaq.txt", "r") as f_hand:
            self.searchquery = f_hand.readline().strip()

        with open("ehist.txt", "r", encoding='utf-8') as f:
            self.hislst = f.readlines()
            self.hislst = [i.strip() for i in self.hislst]


    def process_events(self, event):
        command = self.entry1.get()
        self.set_text("")
        self.last_command = command
        command.strip()
        coms = command.split("|")
        for item in coms:
            self.eventHandler(item)

    def up_arrow(self, e=None):
        self.inx += 1 
        if self.inx >= MAXHIST:
            self.inx = 0
        self.set_text(self.hislst[self.inx])

    def down_arrow(self, e=None):
        self.inx -= 1
        if self.inx < 0:
            self.inx = 0
        self.set_text(self.hislst[self.inx])

    def clear_entry(self, e=None):
        self.set_text("")
        self.inx = MAXHIST


    def eventHandler(self, stext):
        ''' HANDLES COMMAND OR SEARCH FROM THE ENTRY FIELD '''
        global b_deco  # bool for window decoration
        global b_topm  # bool for window topmost
        global leng  # integer for Entry widget length

        if stext == "":
            return

        # save last ten commands
        if stext != "x":
            self.hislst.insert(0, stext)
            self.hislst.pop()
            self.inx = MAXHIST

        with open("serv.txt", "r", encoding='utf-8') as fi:
            for srv in fi:
                if srv.startswith(stext):  # tag
                    ary = srv.split(",")
                    action = ary[1].strip()
                    if action.startswith("http"):
                        webbrowser.get('windows-default').open(action)
                        return
                    else:
                        if " " in action:  # process with arguments
                            cmd = action.split(" ")
                            subprocess.Popen(cmd)  # needs fullpath
                            return
                        else:
                            # may open a "dos" window
                            os.system(action) # process w/o args
                            return

        if stext.lower() == "x":
            f = open("ehist.txt", "w")
            for line in self.hislst:
                f.write(line + "\n")
            f.close()
            root.destroy()
            quit()  # Note: must use "winset" to save geometry

        elif stext.lower().startswith("u:"):
            stext = stext[2:]
            self.writehist(stext)  # save to history (hist.txt)
            if stext.startswith("http"):
                webbrowser.open(stext)
            else:
                return

        elif len(stext) > 1 and stext[1] == ':':
            # try to locate the service from the serv.txt file
            with open("serv.txt", "r", encoding='utf-8') as fi:
                for srv in fi:
                    if srv.startswith(stext[:1]):
                        ary = srv.split(",")
                        webbrowser.open(ary[2] + stext[2:])

        elif stext.startswith("http"):
            self.writeurl(stext)  # write to top of urls.txt

        elif stext.lower() == "hist":
            self.onHistView()

        elif stext.lower() == "list":
            self.onListView()

        elif stext.lower() == "serv":
            self.onServView()

        elif stext.lower() == "sc":
            with open("clip.txt", "a") as f_hand:
                f_hand.write(root.clipboard_get() + "\n\n")

        elif stext.lower() == "ec":
            self.open_editor("clip.txt")

        elif stext.lower() == "es":
            self.open_editor("serv.txt")

        elif stext.lower() == "eh":
            self.open_editor("hist.txt")

        elif stext.lower() == "eu":
            self.open_editor("urls.txt")

        elif stext.lower() == "eq":
            self.openw_editor("seaq.txt")  # wait for changes
            with open("seaq.txt", "r") as f_hand:
                self.searchquery = f_hand.readline().strip()

        elif stext.lower() == "ee":
            self.openw_editor("edit.txt")  # wait for changes
            with open("edit.txt", "r") as f_hand:
                self.editor = f_hand.readline().strip()

        elif stext[0] in "$>@":  # system command or URL
            stext = stext[1:]
            if stext.startswith("http"):  # browse URL
                webbrowser.open(stext)
            else:
                os.system(stext)  # execute a windows command

        elif stext.lower() == "help" or stext.lower() == "about":
            self.open_editor("help.txt")

        elif stext[0] == '=':  # parse a math expression
            stext = stext[1:]
            ans = eval(stext)
            root.clipboard_clear()
            root.clipboard_append(ans)
            self.set_text('=' + str(ans)) # set_text is a user function
            return

        elif stext.lower() == "cap":
            if b_deco:
                b_deco = False
                root.overrideredirect(False) # no caption
            else:
                b_deco = True
                root.overrideredirect(True) # yes caption

        elif stext.lower() == "top":
            if b_topm:
                b_topm = False
                root.attributes("-topmost", False)  # Not on top
            else:
                b_topm = True
                root.attributes("-topmost", True)  # on top

        elif stext.lower() == "winset":
            p = root.geometry().split("+")  # WxH+left+top
            t = self.entry1.configure('width')  # ('width','width','Width',20,25)
            leng = t[4]  # WIDTH of ENTRY leng
            with open("coor.txt", "w") as f_hand:
                f_hand.write(p[1] + "\n" + p[2] + "\n")  # left and top (p[1], p[2])
                f_hand.write(str(int(b_deco)) + "\n")
                f_hand.write(str(int(b_topm)) + "\n")
                f_hand.write(str(leng) + "\n")
        else:
            # Last option remains must be Internet search
            if (stext.find("&") >= 0):
                stext = quote(stext, safe='')
            webbrowser.get('windows-default').open(self.searchquery + stext)
            self.writehist(stext)  # save to history (hist.txt)


    #  OTHER FUNCTIONS

    def saveFromClip(self):
        ''' handle saving of clipboard contents '''
        stext = self.entry1.get()
        if stext != "":
            # then just run for whatever is in stext
            self.process_events(None)
            return
        # assume something was placed in clipboard
        stext = root.clipboard_get()
        if stext == "":
            return
        # assume it is either a URL or some text to save
        if stext.startswith("http"):
            self.writeurl(str(stext))
        else:
            with open("clip.txt", "a") as f_hand:
                f_hand.write(stext + "\n\n")
        root.clipboard_clear()  # clear clipboard contents


    def set_text(self, text):
        ''' helper function to set text into Entry field '''
        self.entry1.delete(0, END)
        self.entry1.insert(0, text.strip())


    def gettagdata(self, url, subs1, subs2):
        r = requests.get(url)
        data = r.text
        i = data.index(subs1) + 7
        j = data.index(subs2)
        return data[i:j]

    def writeurl(self, sline):
        ''' writes a line to the top of urls.txt file '''
        f_hand = open("urls.txt", "r", encoding='utf-8')
        hold = f_hand.readlines()
        f_hand.close()

        # get the page title
        title = self.gettagdata(sline, "<title>", "</title>")
        with open("urls.txt", "w") as f_hand:
            f_hand.write(title + " <=> " + sline + "\n")
            for item in hold:
                f_hand.write(str(item))


    def writehist(self, sline):
        ''' writes a line to the history file '''
        with open("hist.txt", "a") as f_hand:
            f_hand.write(sline + ", " + strftime('%x') + "\n")
        # self.hislst.insert(0, sline)
        # self.hislst.pop()
        # self.inx = MAXHIST


    def onTopClose(self, key=None):
        ''' Close the toplevel window '''
        t.destroy()
        t.update()

    def onHistView(self):
        ''' Launch new window with listbox and hist.txt contents '''
        global t
        t = Toplevel(self)
        t.wm_title("Search History")
        t.geometry("400x300") # WxH+left+top
        t.iconbitmap("icon.ico")
        # l = Label(t, text="This is hist window")
        t.bind("<Escape>", self.onTopClose)
        sbar = Scrollbar(t)
        sbar.pack(side=RIGHT, fill=Y)
        l = Listbox(t, yscrollcommand=sbar.set, exportselection=0)
        f_hand = open("hist.txt", "r", encoding='utf-8')
        items = f_hand.readlines()
        items.reverse()
        f_hand.close()
        for inx, item in enumerate(items):
            item = item[0:item.find(", ")].rstrip()
            l.insert(inx, " " + item)
        l.bind("<<ListboxSelect>>", self.onHistSelect)
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        sbar.config(command=l.yview)

    def onHistSelect(self, val):
        ''' Handle row clicked in history listbox '''
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)
        webbrowser.open(self.searchquery + value)
        self.onTopClose()


    def onListView(self):
        ''' Launch new window with listbox of saved URLs '''
        global t
        t = Toplevel(self)
        t.wm_title("BCB Saved URLs")
        t.geometry("400x300") # WxH+left+top
        t.iconbitmap("icon.ico")
        t.bind("<Escape>", self.onTopClose)
        sbar = Scrollbar(t)
        sbar.pack(side=RIGHT, fill=Y)
        l = Listbox(t, yscrollcommand=sbar.set)
        f_hand = open("urls.txt", "r", encoding='utf-8')
        items = f_hand.readlines()
        f_hand.close()
        for inx, item in enumerate(items):
            l.insert(inx, item.rstrip())
        l.bind("<<ListboxSelect>>", self.onListSelect)
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        sbar.config(command=l.yview)

    def onListSelect(self, val):
        ''' Handle row clicked in URL listbox '''
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)
        # extract just the url
        try:
            i = value.index(" <=> ")
            value = value[i+5:]
        except:
            pass
        webbrowser.open(value)
        self.onTopClose()

    def onServView(self):
        ''' Launch new window with listbox of saved URLs '''
        global t
        t = Toplevel(self)
        t.wm_title("BCB User Commands")
        t.geometry("400x300") # WxH+left+top
        t.iconbitmap("icon.ico")
        t.bind("<Escape>", self.onTopClose)
        sbar = Scrollbar(t)
        sbar.pack(side=RIGHT, fill=Y)
        l = Listbox(t, yscrollcommand=sbar.set)
        f_hand = open("serv.txt", "r", encoding='utf-8')
        items = f_hand.readlines()
        f_hand.close()
        for inx, item in enumerate(items):
            if item.startswith("--- SERVICES"):
                break
            if item.startswith("---"):
                continue
            l.insert(inx, item.rstrip())
        l.bind("<<ListboxSelect>>", self.onServSelect)
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        sbar.config(command=l.yview)

    def onServSelect(self, val):
        ''' Handle row clicked in URL listbox '''
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)
        lstv = value.split(",")
        value = lstv[0].strip()
        self.set_text(value)
        self.process_events(None)
        self.onTopClose()


    def open_editor(self, fin):
        '''
            Launch text editor with 'fin' file
            Does not wait for process to finish
        '''
        subprocess.Popen([self.editor, fin])

    def openw_editor(self, fin):
        '''
            Launch text editor with 'fin' file
            Waits for process to finish
        '''
        subprocess.call([self.editor, fin])

# END OF Application class

styl = open("style").read().strip()
root = ThemedTk(theme=styl)

# change working directory to path for this file
p = os.path.realpath(__file__)
os.chdir(os.path.dirname(p))

# SET POSITION FROM LAST SAVE POSITION
lcoor = tuple(open("coor.txt", 'r'))  # no relative path for this
leng = int(lcoor[4])
root.geometry('+%d+%d'%(int(lcoor[0].strip()), int(lcoor[1].strip())))
root.title("BCB")
root.iconphoto(False, PhotoImage(file='icon.png'))
if int(lcoor[2]) == 0:
    b_deco = False
    root.overrideredirect(False)  # no caption
else:
    b_deco = True
    root.overrideredirect(True) # yes caption
if int(lcoor[3]) == 0:
    b_topm = False
    root.attributes("-topmost", False)  # Not on top
else:
    b_topm = True
    root.attributes("-topmost", True)  # on top

root.iconbitmap("icon.ico")
app = Application(root)
app.mainloop()
