#Imports
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from sheetsapi import data_ss as dataspread
from datetime import datetime
import threading
#Logging
import logging
logging.getLogger().setLevel(logging.DEBUG)
special_shots_master_list = {}

def compare_scores(first,second):
    values = []
    for hole, score in enumerate(second):
        current_hole_score = first[hole]
        if score == '':
            values.append(current_hole_score)
        else:  # they actually marked an improvement
            if current_hole_score != '':
                if int(score) < int(current_hole_score):
                    values.append(score)
                else:
                    values.append(current_hole_score)
            else:
                values.append(score)
    return values
def error(progressbar,warning):
    window.update()
    progressbar.destroy()
    stringvar.set(warning)
    confirm.config(state=tk.NORMAL)
    logging.warning(warning)
    ringer_lastnames = None
    ringer_firstnames = None
    ringer2_lastnames = None
    ringer2_firstnames = None
    return
def parse_hole_data(data):
    do = True
    if data == '':
        do = False
        newlist = []
    if do:
        data = data.split(" ")
        newlist = []
        for index in data:
            index = index.replace(',','')
            newlist.append(index)
    return newlist

def autofill(progressbar):
    window.update()
    progressbar.start()
    stringvar.set("Starting Autofill process...")
    index = None
    ph = [year.get(),month.get(),day.get()]
    time = [hour.get(),minute.get()]
    if "" in ph:
        window.update()
        progressbar.destroy()
        stringvar.set("Please select a valid date!")
        confirm.config(state=tk.NORMAL)
        ringer_lastnames = None
        ringer_firstnames = None
        ringer2_lastnames = None
        ringer2_firstnames = None
        logging.warning("Invalid Date Submitted!")
        return
    if "" in time: use_time = False
    else:
        use_time = True
        input_hour = int(hour.get())
        input_minute = int(minute.get())
    input_year = int(year.get())
    input_month = int(month.get())
    input_day = int(day.get())
    if "" in time:
        try: input_date = datetime(input_year,input_month,input_day)
        except ValueError:
            window.update()
            progressbar.destroy()
            stringvar.set("Please select a valid date!")
            confirm.config(state=tk.NORMAL)
            logging.warning("Invalid Date Submitted!")
            return
    else:
        try: input_date = datetime(input_year,input_month,input_day,input_hour,input_minute)
        except ValueError:
            window.update()
            progressbar.destroy()
            stringvar.set("Please select a valid date!")
            confirm.config(state=tk.NORMAL)
            logging.warning("Invalid Date Submitted!")
            ringer_lastnames = None
            ringer_firstnames = None
            ringer2_lastnames = None
            ringer2_firstnames = None
            return
    timestamps = dataspread.get_timestamps(dataspread)
    window.update()
    stringvar.set("Determining data set...")
    for timestamp in timestamps:
        if timestamp == '':
            continue
        if use_time:
            sep = timestamp.replace(" ","/")
            sep = sep.replace(":","/")
            sep = sep.split("/")
            timestamp_date = datetime(int(sep[2]),int(sep[0]),int(sep[1]),int(sep[3]),int(sep[4]))
        else:
            sep = timestamp.split(" ")
            sep = sep[0].split("/")
            timestamp_date = datetime(int(sep[2]),int(sep[0]),int(sep[1]))
        if timestamp_date >= input_date:
            index = timestamps.index(timestamp)
            break
    if index == None: #invalid date
        window.update()
        progressbar.destroy()
        stringvar.set("Invalid Date! There aren't any submissions after this date.")
        confirm.config(state=tk.NORMAL)
        logging.warning("Invalid Date Submitted!")
        ringer_lastnames = None
        ringer_firstnames = None
        ringer2_lastnames = None
        ringer2_firstnames = None
        return
    window.update()
    stringvar.set("Pulling Google Forms answers...")
    specials_raw_data,scores_raw_data,pb_raw = dataspread.get_raw_data(dataspread,index)
    ringer_lastnames,ringer_firstnames,ringer2_lastnames,ringer2_firstnames = dataspread.get_names(dataspread)
    window.update()
    stringvar.set("Updating Chips, Birdies and Sand save counts...")
    all_current_specials = dataspread.get_player_specials(dataspread)
    for phdex, r_lastname in enumerate(ringer2_lastnames):
        r_firstname = ringer_firstnames[phdex]
        batch = {
        'range': '',
        'values': []}
        values = []
        for spdex,name in enumerate(specials_raw_data):
            special_shots = specials_raw_data[name]
            if name == " ":
                continue
            name = name.split(" ")
            if name[1] == r_lastname and name[0] == r_firstname:
                current_specials = all_current_specials[phdex][1:55]
                values = current_specials
                chips_list = parse_hole_data(special_shots[0])
                birdies_list = parse_hole_data(special_shots[1])
                sandies_list = parse_hole_data(special_shots[2])
                for hole,chip in enumerate(chips_list):
                    index = 2*int(chip) - (3-int(chip))
                    if values[index] =='': values[index] = "0"
                    values[index] = str(int(values[index])+1)
                for hole,birdie in enumerate(birdies_list):
                    index = 2*int(birdie) - (2-int(birdie))
                    if values[index] =='': values[index] = "0"
                    values[index] = str(int(values[index])+1)
                for hole,sandie in enumerate(sandies_list):
                    index = 2*int(sandie) - (1-int(sandie))
                    if values[index] =='': values[index] = "0"
                    values[index] = str(int(values[index])+1)
                batch['range'] = 'C'+str(phdex+3)+':'+'BD'+str(phdex+3)
                batch['values'] = [values]
                dataspread.batch_update_ringerboard2(dataspread,batch)
                break
    ringerboard_scores = dataspread.get_current_scores(dataspread)
    window.update()
    stringvar.set("Updating Best Scores...")
    empty = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    for phdex,r_lastname in enumerate(ringer_lastnames):
        r_firstname = ringer_firstnames[phdex]
        batch = {
        'range': '',
        'values': []}
        values = []
        for spdex,name in enumerate(scores_raw_data):
            if name == " ":
                continue
            name = name.split(" ")
            fullname = name[0] + " " + name[1]
            if len(name) == 3: processed = True
            else: processed = False
            if name[1] == r_lastname and name[0] == r_firstname:
                if processed:
                    dexs = []
                    for name2 in scores_raw_data:
                        name2 = name2.split(" ")
                        try: namedex = int(name2[2])
                        except IndexError: namedex=0
                        dexs.append(namedex)
                    count = max(dexs)
                    if int(name[2]) != count:
                        continue
                    for i in range(count):
                        if i == 0:
                            n = scores_raw_data[fullname]
                            if ringerboard_scores[0][phdex] == empty: values = n
                            else: values = compare_scores(ringerboard_scores[0][phdex],n)
                        else:
                            p = values
                            n = scores_raw_data[fullname+" "+str(i+1)]
                            values = compare_scores(p,n)
                else:
                    p = ringerboard_scores[0][phdex]
                    n = scores_raw_data[fullname]
                    values = compare_scores(p,n)
                batch['range'] = "D"+str(phdex+3)+":"+"U"+str(phdex+3)
                batch['values'] = [values]
                dataspread.batch_update_ringerboard(dataspread,batch)
    ixs=[]
    batch=[]
    window.update()
    stringvar.set("Updating Achievements...")
    for phdex, r_lastname in enumerate(ringer2_lastnames):
        r_firstname = ringer2_firstnames[phdex]
        for spdex,name in enumerate(pb_raw):
            new_pb = pb_raw[name]
            if name == " ":
                continue
            name = name.split(" ")
            if name[1] == r_lastname and name[0] == r_firstname:
                batch.append(new_pb)
                ixs.append(phdex)
    dataspread.batch_update_cells(dataspread,batch,ixs)
    window.update()
    progressbar.destroy()
    stringvar.set("All form submissions filled!")
    confirm.config(state=tk.NORMAL)
    ringer_lastnames = None
    ringer_firstnames = None
    ringer2_lastnames = None
    ringer2_firstnames = None

def confirm_button():
    confirm.config(state=tk.DISABLED)
    progressbar = ttk.Progressbar(window,orient='horizontal',length=360,mode='indeterminate')
    main = threading.Thread(target=autofill,args=(progressbar,))
    progressbar.pack()
    main.start()


window = tk.Tk()
window.geometry("520x320")
window.title("MWGC Ladies Ringerboard App by Connor Loi")
window.resizable(False,False)


titleFont = tkFont.Font(family="Lucida Grande", size=25)
headerFont = tkFont.Font(family="Lucida Grande",size=20)
subHeaderFont = tkFont.Font(family="Lucida Grande",size=17)
labelFont = tkFont.Font(family="Lucida Grande",size=14)
logging.info("Built Window")
stringvar = tk.StringVar()
title = tk.Label(window,text="Ladies Ringerboard Autofill",anchor="n",font=titleFont)
title.pack()
header = tk.Label(window, text="Date", anchor="n",font=headerFont)
header.pack()

gridframe = tk.Frame(window)
gridframe.pack()

yframe = tk.Frame(gridframe)
yframe.grid(row=0,column=0,padx=5,pady=3)
yearlabel = tk.Label(yframe,text="Year", font=labelFont)
yearlabel.pack()
year = tk.Entry(yframe, width=10)
year.pack()

mframe = tk.Frame(gridframe)
mframe.grid(row=0,column=1,padx=5,pady=3)
monthlabel = tk.Label(mframe,text="Month", font=labelFont)
monthlabel.pack()
month = tk.Entry(mframe, width=10)
month.pack()

dframe = tk.Frame(gridframe)
dframe.grid(row=0,column=2,padx=5,pady=3)
daylabel = tk.Label(dframe,text="Day", font=labelFont)
daylabel.pack()
day = tk.Entry(dframe,width=10)
day.pack()

header2 = tk.Label(window, text="Time (optional)", anchor="n", font=subHeaderFont)
header2.pack()
gridframe2 = tk.Frame(window)
gridframe2.pack()

hframe = tk.Frame(gridframe2)
hframe.grid(row=0,column=0,padx=5,pady=3)
hourlabel = tk.Label(hframe,text="Hour",font=labelFont)
hourlabel.pack()
hour = tk.Entry(hframe,width=10)
hour.pack()

minframe = tk.Frame(gridframe2)
minframe.grid(row=0,column=1,padx=5,pady=3)
minlabel = tk.Label(minframe,text="Minute",font=labelFont)
minlabel.pack()
minute = tk.Entry(minframe,width=10)
minute.pack()

confirm = tk.Button(master=window, text="Confirm", command=confirm_button,state=tk.NORMAL)
confirm.pack()
label = tk.Label(master=window,textvariable=stringvar,font=labelFont)
label.pack()
logging.info("Packed and loaded GUI")

photo = tk.PhotoImage(file = "MWGC_logo.png")
window.iconphoto(False,photo)
window.mainloop()