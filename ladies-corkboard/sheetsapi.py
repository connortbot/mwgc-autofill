import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
scope = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']

#use this line when compiling
#creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/MonkeyDumpling/Desktop/ladies-corkboard/dist/main/client_secret.json', scope)

#use this line in IDE
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
datasheet = client.open("Google Form Responses").sheet1
ringerboard = client.open("Test").sheet1
ringerboard_specials = client.open("Test").get_worksheet(1)

specials_masterlist = {}
score_masterlist = {}

class data_ss:
    def get_timestamps(self):
        timestamps = datasheet.col_values(1)
        timestamps.remove("Timestamp")
        return timestamps
    def get_raw_data(self,timedex):
        master = datasheet.batch_get(["B2:X150"])[0]
        for index,entry in enumerate(master):
            if index >= timedex:
                firstname = entry[0].title()
                lastname = entry[1].title()
                entry = entry[2:5]
                specials_masterlist[firstname + " " + lastname] = entry
        for index, entry in enumerate(master):
            if index >= timedex:
                firstname = entry[0].title()
                lastname = entry[1].title()
                entry = entry[5:]
                score_masterlist[firstname + " " + lastname] = entry
        return specials_masterlist,score_masterlist
    def get_names(self):
        rnames = ringerboard.batch_get(["A3:B100"],major_dimension='COLUMNS')[0]
        rfirstnames = rnames[1]
        rlastnames = rnames[0]
        rsnames = ringerboard_specials.batch_get(["A3:B100"],major_dimension='COLUMNS')[0]
        rsfirstnames = rsnames[1]
        rslastnames = rsnames[0]
        print(rslastnames)
        print(rsnames)
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
        sc = ringerboard.batch_get(["D3:U4"])
        return sc
    def batch_update_ringerboard(self,batch):
        ringerboard.batch_update([batch],value_input_option='USER_ENTERED')
    def batch_update_ringerboard2(self,batch):
        ringerboard_specials.batch_update([batch],value_input_option='USER_ENTERED')
#bruh = data_ss.get_specials_data(data_ss,4)