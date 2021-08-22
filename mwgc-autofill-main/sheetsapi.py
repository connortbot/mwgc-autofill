import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
scope = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']

#use this line when compiling
#creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\MonkeyDumpling\Desktop\mwgc-autofill-main\dist\main\client_secret.json', scope)

#use this line in IDE
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

client = gspread.authorize(creds)
datasheet = client.open("Google Form Responses").sheet1
ringerboard = client.open("Test").sheet1
ringerboard_specials = client.open("Test").get_worksheet(1)

specials_masterlist = {}
score_masterlist = {}
pb_masterlist = {}

class data_ss:
    def get_timestamps(self):
        timestamps = datasheet.col_values(1)
        timestamps.remove("Timestamp")
        return timestamps
    def get_raw_data(self,timedex):
        master = datasheet.batch_get(["B2:Y150"])[0]
        for index,entry in enumerate(master):
            if index >= timedex:
                firstname = entry[0].title()
                lastname = entry[1].title()
                entry = entry[2:5]
                specials_masterlist[firstname + " " + lastname] = entry
        processed = []
        for index, entry in enumerate(master):
            if index >= timedex:
                firstname = entry[0].title()
                lastname = entry[1].title()
                fullname = firstname+" "+lastname
                count = 0
                if fullname in processed: #we've made an entry with this person before
                    for name in processed:
                        name = name.split(" ")
                        if len(name) == 3: name = name[:3]
                        name = name[0]+" "+name[1]
                        if name == fullname: count += 1
                    lastname = lastname+" "+str(count+1)
                if len(entry) == 24:
                    pb = entry[23]
                    pb_masterlist[firstname+" "+lastname] = pb
                else:
                    pb_masterlist[firstname+" "+lastname] = 0
                entry = entry[5:22]
                score_masterlist[firstname + " " + lastname] = entry
                processed.append(firstname+" "+lastname)
        return specials_masterlist,score_masterlist,pb_masterlist
    def get_names(self):
        rnames = ringerboard.batch_get(["A3:B100"],major_dimension='COLUMNS')[0]
        rfirstnames = rnames[1]
        rlastnames = rnames[0]
        rsnames = ringerboard_specials.batch_get(["A3:B100"],major_dimension='COLUMNS')[0]
        rsfirstnames = rsnames[1]
        rslastnames = rsnames[0]
        return rlastnames,rfirstnames,rslastnames,rsfirstnames
    def get_cell(self,cell):
        data = ringerboard.get(cell)
        return data
    def set_cell(self,cell,value):
        ringerboard.update(cell,value)
    def set_cell2(self,cell,value):
        ringerboard_specials.update(cell,value)
    def get_player_specials(self):
        sp = ringerboard_specials.batch_get(["B3:BE100"])[0]
        ph = []
        for row in sp:
            row = row[1:55]
            ph.append(row)
        return sp
    def get_current_scores(self):
        sc = ringerboard.batch_get(["D3:V100"])[0]
        ph = []
        for row in sc:
            row = row[:18]
            ph.append(row)
        ph = [ph]
        return ph
    def batch_update_ringerboard(self,batch):
        ringerboard.batch_update([batch],value_input_option='USER_ENTERED')
    def batch_update_ringerboard2(self,batch):
        ringerboard_specials.batch_update([batch],value_input_option='USER_ENTERED')
    def batch_update_cells(self,batch,ixs):
        cell_list = ringerboard_specials.range("BH3:BH100")
        for index,cell in enumerate(cell_list):
            for phdex,rdex in enumerate(ixs):
                if rdex==index: #This cell is cell we want to update
                    cell_list[index].value = batch[phdex]
        ringerboard_specials.update_cells(cell_list,value_input_option='USER_ENTERED')