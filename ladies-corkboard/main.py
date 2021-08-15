#Imports
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from sheetsapi import data_ss as dataspread
from time import sleep
from datetime import datetime
import threading
#Logging
import logging
logging.getLogger().setLevel(logging.DEBUG)
special_shots_master_list = {}

ref = [[0,'C','F','I','L','O','R','U','X','AA','AD','AG','AJ','AM','AP','AS','AV','AY','BB'],
[0,'D','G','J','M','P','S','V','Y','AB','AE','AH','AK','AN','AQ','AT','AW','AZ','BC'],
[0,'E','H','K','N','Q','T','W','Z','AC','AF','AI','AL','AO','AR','AU','AX','BA','BD']]

def parse_hole_data(data):
    data = data.split(",")
    newlist = []
    for index,entry in enumerate(data):
        if index != 0:
            entry = entry[1:]
        entry = entry.split(" ")
        entry.remove("Hole")
        entry = entry[0]
        newlist.append(entry)
    return newlist

def autofill(progressbar):
    window.update()
    progressbar.start()
    stringvar.set("Starting Autofill process...")
    index = 0
    ph = [year.get(),month.get(),day.get()]
    if "" in ph: return
    input_year = int(year.get())
    input_month = int(month.get())
    input_day = int(day.get())
    try: input_date = datetime(input_year,input_month,input_day)
    except ValueError:
        window.update()
        progressbar.destroy()
        stringvar.set("Please select a valid date!")
        confirm.config(state=tk.NORMAL)
        logging.warning("Invalid Date Submitted!")
        return
    timestamps = dataspread.get_timestamps(dataspread)
    window.update()
    stringvar.set("Determining data set...")
    for timestamp in timestamps:
        if timestamp == '':
            continue
        sep1 = timestamp.split(" ")
        sep2 = sep1[0].split("/")
        timestamp_date = datetime(int(sep2[2]),int(sep2[0]),int(sep2[1]))
        if timestamp_date >= input_date:
            index = timestamps.index(timestamp)
            break
    if index == 0: #invalid date
        window.update()
        progressbar.destroy()
        stringvar.set("Invalid Date! There aren't any submissions after this date.")
        confirm.config(state=tk.NORMAL)
        logging.warning("Invalid Date Submitted!")
        return
    window.update()
    stringvar.set("Pulling Google Forms answers...")
    specials_raw_data,scores_raw_data = dataspread.get_raw_data(dataspread,index)
    ringer_lastnames,ringer_firstnames,ringer2_lastnames,ringer2_firstnames = dataspread.get_names(dataspread)
    window.update()
    stringvar.set("Updating Chips, Birdies and Sand save counts...")
    all_current_specials = dataspread.get_player_specials(dataspread)
    print(ringer2_lastnames)
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
            print(name)
            print(r_lastname)
            print(r_firstname)
            if name[1] == r_lastname and name[0] == r_firstname:
                current_specials = all_current_specials[phdex][1:55]
                values = current_specials
                try: chips_list = parse_hole_data(special_shots[0])
                except ValueError: chips_list = []
                try: birdies_list = parse_hole_data(special_shots[1])
                except ValueError: birdies_list = []
                try: sandies_list = parse_hole_data(special_shots[2])
                except ValueError: sandies_list = []
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
    for phdex,r_lastname in enumerate(ringer_lastnames):
        r_firstname = ringer_firstnames[phdex]
        batch = {
        'range': '',
        'values': []}
        values = []
        for spdex,name in enumerate(scores_raw_data):
            new_scores = scores_raw_data[name]
            if name == " ":
                continue
            name = name.split(" ")
            if name[1] == r_lastname and name[0] == r_firstname:
                try: player_scores = ringerboard_scores[0][phdex]
                except IndexError:
                    player_scores = []
                    for i in range(18):
                        player_scores.append('')
                for hole,score in enumerate(new_scores):
                    current_hole_score = player_scores[hole]
                    if score == '': values.append(current_hole_score)
                    else: #they actually marked an improvement
                        if current_hole_score != '':
                            if int(score)<int(current_hole_score):
                                values.append(score)
                            else: values.append(current_hole_score)
                        else: values.append(score)
                range_u = "D"+str(phdex+3)+":"+"U"+str(phdex+3)
                batch['range'] = range_u
                batch['values'] = [values]
                dataspread.batch_update_ringerboard(dataspread,batch)
    window.update()
    progressbar.destroy()
    stringvar.set("All form submissions filled!")
    confirm.config(state=tk.NORMAL)

def confirm_button():
    confirm.config(state=tk.DISABLED)
    progressbar = ttk.Progressbar(window,orient='horizontal',length=360,mode='indeterminate')
    main = threading.Thread(target=autofill,args=(progressbar,))
    progressbar.pack()
    main.start()


window = tk.Tk()
window.geometry("400x320")
window.title("MWGC Ladies Ringerboard App by Connor Loi")
window.resizable(False,False)


titleFont = tkFont.Font(family="Lucida Grande", size=25)
headerFont = tkFont.Font(family="Lucida Grande",size=20)
labelFont = tkFont.Font(family="Lucida Grande",size=14)
logging.info("Built Window")
stringvar = tk.StringVar()
title = tk.Label(window,text="Ladies Ringerboard Autofill",anchor="n",font=titleFont)
title.pack()
header = tk.Label(window, text="Date", anchor="n",font=headerFont)
header.pack()
yearlabel = tk.Label(window,text="Year", font=labelFont)
yearlabel.pack()
year = tk.Entry(window, width=10)
year.pack()
monthlabel = tk.Label(window,text="Month", font=labelFont)
monthlabel.pack()
month = tk.Entry(window, width=10)
month.pack()
daylabel = tk.Label(window,text="Day", font=labelFont)
daylabel.pack()
day = tk.Entry(window,width=10)
day.pack()
confirm = tk.Button(master=window, text="Confirm", command=confirm_button,state=tk.NORMAL)
confirm.pack()
label = tk.Label(master=window,textvariable=stringvar,font=labelFont)
label.pack()
logging.info("Packed and loaded GUI")

window.mainloop()