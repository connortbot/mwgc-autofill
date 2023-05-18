import gspread
from oauth2client.service_account import ServiceAccountCredentials

import os
import sys
import time

import pickle
from time import sleep
scope = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']

sheetnames = {
    "Datasheet": '',
    "Ringerboard": '',
    "Row Number": '',
}

try:
    with open('userdata.pickle','rb') as f:
        sheetnames = pickle.load(f)
except:
    with open('userdata.pickle', 'wb') as f:
        pickle.dump(sheetnames, f)

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.realpath(__file__))
client_secret_path = os.path.join(script_dir, 'client_secret.json')
creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret_path, scope)

client = gspread.authorize(creds)
datasheet = ''
ringerboard = ''
ringerboard_specials = ''

specials_masterlist = {}
score_masterlist = {}
pb_masterlist = {}


max_retries = 9

def exponential_backoff(func_name,err,iter):
    if err.response.status_code == 429:
        sleep_time = (2 ** iter)
        print(f"RETRYING {iter} for {sleep_time} seconds: CATCH 429 => {func_name}")
        time.sleep(sleep_time)
    else:
        raise err




class data_ss:
    def get_timestamps(self):
        global datasheet
        global ringerboard
        global ringerboard_specials
        try: datasheet = client.open(sheetnames["Datasheet"]).sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            return False
        try:
            ringerboard = client.open(sheetnames["Ringerboard"]).sheet1
            ringerboard_specials = client.open(sheetnames["Ringerboard"]).get_worksheet(1)
        except gspread.exceptions.SpreadsheetNotFound:
            return False
        timestamps = datasheet.col_values(1)
        timestamps.remove("Timestamp")
        timestamps.remove("Timestamp")
        return timestamps


    def update(self,cell,text):
        for n in range(max_retries + 1):
            try:
                ringerboard.update(cell,text)
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ update [SHEET1]",e,n)
        for n in range(max_retries + 1):
            try:
                ringerboard_specials.update(cell, text)
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ update [SHEET2]",e,n)
    def get_raw_data(self,timedex):
        for n in range(max_retries + 1):
            try:
                master = datasheet.batch_get(["B3:Z5000"])[0]
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ get_raw_data",e,n)
        processed = []
        for index,entry in enumerate(master):
            if index >= timedex:
                firstname = entry[0].upper().replace("-","")
                if " " in firstname: firstname = firstname.replace(" ", "")
                lastname = entry[1].upper().replace("-","")
                if " " in lastname: lastname = lastname.replace(" ","")
                fullname = firstname + " " + lastname
                count = 0
                if fullname in processed:
                    for name in processed:
                        name = name.split(" ")
                        if len(name) == 3: name = name[:3]
                        name = name[0]+" "+name[1]
                        if name == fullname: count += 1
                    lastname = lastname+" "+str(count+1)
                entry = entry[2:5]
                specials_masterlist[firstname + " " + lastname] = entry
                processed.append(firstname+" "+lastname)
        processed = []
        for index, entry in enumerate(master):
            if index >= timedex:
                firstname = entry[0].upper().replace("-", "")
                if " " in firstname: firstname = firstname.replace(" ", "")
                lastname = entry[1].upper().replace("-", "")
                if " " in lastname: lastname = lastname.replace(" ", "")
                fullname = firstname+" "+lastname
                count = 0
                if fullname in processed: #we've made an entry with this person before
                    for name in processed:
                        name = name.split(" ")
                        if len(name) == 3: name = name[:3]
                        name = name[0]+" "+name[1]
                        if name == fullname: count += 1
                    lastname = lastname+" "+str(count+1)
                if len(entry) == 25:
                    pb = entry[23]
                    pb_masterlist[firstname+" "+lastname] = pb
                else:
                    pb_masterlist[firstname+" "+lastname] = 0
                entry = entry[5:23]
                score_masterlist[firstname + " " + lastname] = entry
                processed.append(firstname+" "+lastname)
        return specials_masterlist,score_masterlist,pb_masterlist
    def get_names(self):
        rownum = sheetnames["Row Number"]
        for n in range(max_retries + 1):
            try:
                rnames = ringerboard.batch_get(["A3:B"+rownum],major_dimension='COLUMNS')[0]
                rfirstnames = rnames[1]
                rlastnames = rnames[0]
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ get_names [SHEET1]",e,n)
        for n in range(max_retries + 1):
            try:
                rsnames = ringerboard_specials.batch_get(["A3:B"+rownum],major_dimension='COLUMNS')[0]
                rsfirstnames = rsnames[1]
                rslastnames = rsnames[0]
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ get_names [SHEET2]",e,n)
        return rlastnames,rfirstnames,rslastnames,rsfirstnames
    def get_player_specials(self):
        rownum = sheetnames["Row Number"]
        for n in range(max_retries + 1):
            try:
                sp = ringerboard_specials.batch_get(["B3:BE"+rownum])[0]
                ph = []
                for row in sp:
                    row = row[1:55]
                    ph.append(row)
                return sp
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ get_player_specials",e,n)
    def get_current_scores(self):
        rownum = sheetnames["Row Number"]
        for n in range(max_retries + 1):
            try:
                sc = ringerboard.batch_get(["D3:V"+rownum])[0]
                ph = []
                for row in sc:
                    row = row[:18]
                    ph.append(row)
                ph = [ph]
                return ph
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ get_current_scores",e,n)
    def get_current_pb(self):
        rownum = sheetnames["Row Number"]
        for n in range(max_retries + 1):
            try:
                pbs = ringerboard_specials.batch_get(["BH1:BH"+rownum])[0]
                pbs = pbs[2:]
                if len(pbs) < (int(rownum)-2):
                    for i in range((int(rownum)-2)-len(pbs)):
                        pbs.append([])
                return pbs
            except gspread.exceptions.APIError as e:
                exponential_backoff("READ get_current_pb",e,n)
    def batch_update_ringerboard(self,batch):
        for n in range(max_retries + 1):
            try:
                ringerboard.batch_update([batch],value_input_option='USER_ENTERED')
                return
            except gspread.exceptions.APIError as e:
                exponential_backoff("WRITE batch_update_ringerboard",e,n)
        raise Exception(f"Still receiving rate limit errors after {max_retries} retries.")
    def batch_update_ringerboard2(self,batch):
        for n in range(max_retries + 1):
            try:
                ringerboard_specials.batch_update([batch],value_input_option='USER_ENTERED')
                return
            except gspread.exceptions.APIError as e:
                exponential_backoff("WRITE batch_update_ringerboard2",e,n)
        raise Exception(f"Still receiving rate limit errors after {max_retries} retries.")
    def batch_update_cells(self,batch,ixs):
        rownum = sheetnames["Row Number"]
        cell_list = ringerboard_specials.range("BH3:BH"+rownum)
        for index,cell in enumerate(cell_list):
            for phdex,rdex in enumerate(ixs):
                if rdex==index: #This cell is cell we want to update
                    cell_list[index].value = batch[phdex]
        for n in range(max_retries + 1):
            try:
                ringerboard_specials.update_cells(cell_list,value_input_option='USER_ENTERED')
                return
            except gspread.exceptions.APIError as e:
                exponential_backoff("WRITE batch_update_cells",e,n)
        raise Exception(f"Still receiving rate limit errors after {max_retries} retries.")


    def change_googleforms_responses_sheet(self,name):
        global sheetnames
        with open('userdata.pickle','rb') as f:
            sheetnames = pickle.load(f)
        sheetnames['Datasheet'] = name
        with open('userdata.pickle', 'wb') as f:
            pickle.dump(sheetnames, f)
    def change_ringerboard_sheet(self,name):
        global sheetnames
        with open('userdata.pickle','rb') as f:
            sheetnames = pickle.load(f)
        sheetnames['Ringerboard'] = name
        with open('userdata.pickle', 'wb') as f:
            pickle.dump(sheetnames, f)
    def change_row_number(self,num):
        global sheetnames
        with open('userdata.pickle', 'rb') as f:
            sheetnames = pickle.load(f)
        sheetnames['Row Number'] = num
        with open('userdata.pickle', 'wb') as f:
            pickle.dump(sheetnames, f)
    def get_sheetnames(self):
        return sheetnames
