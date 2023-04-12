import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
#use this line when compiling
#creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\MonkeyDumpling\Desktop\mwgc-autofill-main\dist\main\client_secret.json', scope)
#use this line in IDE
#creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client_secret = {
  "type": "service_account",
  "project_id": "sheetcrafter-316822",
  "private_key_id": "ed900d99a2ea0081fd0bd8874f2e97812d943d1e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDt/wgu3nuoQEMW\nytLEURioUZrIB1g3stkLDa2/nDhHq1c1fL2jD/+ZQSmG4pVAxjAUU8cTEIE6G6p5\nj3eD9d5bGEPOUYhxr14qhQJ5HXdsqcjT62hWPCbLjzsgL2N1oHZVJavO1nYuRoy6\nL+5i8H22AEIxOJe2/7eGTzvtW6pNYOGt/fI3SyTgQ9VEiTZOe24G5kWLiW16nsVP\nPIeEuy29fWAC414tnC0CvIRN3DGDysi/OusMe+ehAUC51iN/sYJlvB/GOX0dB+7n\n3ZW5514xGyRsmOb0gPWU1/VnSXY+pfefn8dmjiwGS+DwZJgjzpVo1yep8n74ZkWn\nk3qhgq8rAgMBAAECggEANcdQOQ8LEDzdLBROxg+xK6+s8xA9zfA6/TVtEoQhb4h3\nH139mBAwaJgB4znmEgn2qVE5BcTP/qprviY+EnKHeTwlbkScOVwwQhlmMqoG52YC\nPGjQXdQfzBWkfaRXrCfDNYBar1VkxRYqDJRyIKdJMMwkKO0p0y87cD0NRJhXBj6z\nipI5+7BVuZnDZsedYOrZqlmXWH8EMnYWOpLl5nuGPRAwquRcQpW4kLr+ZZYQt4SD\nMKeO4Tg8ozw1ltORU5yTYPtE+hkdf4iEvW0+U0/9mLLvLoWnOt/WC/WpcWkdL+xF\nWOx3D5yQ9BOpGTXZSDXdKdp/YfEvTvItEX+tn+2XAQKBgQD81K3cZjqb7z0F8LrI\nVaVYqpOdqLTpp2A2jqftpZoSYX4R+9kp502P+mi3HyGj9NUR9hV3wlpY8VTiJ3Cb\neWeMmevtt0oyXJ03mdfA3NhRKLB2KDN/4H4AqCJcd57W/ucP6nWwM1zyE8mSZubb\n5HGJFZmlf/A3nCLxYPDyd5YZgQKBgQDw+r/eiPS2nUOA9PzyEYSQ8L4mecWnUu/b\nM0aua0QVNl+zWAuVon9yK7iUzOCl1hdKPTbQeBymf88RKTiZsEWEgZcC9njrSGT4\n23I9wAdgjPraxdM62XXG5LpYJOIEEJ0w8suIPKeURuR5tFQm8MZ03Py7FPYJDns8\nAsnkSramqwKBgQDsrZOL7M8UxmJTu0S+4R4F4LiLMDEbQaoZqHWfTBTs/ALuhtqG\nFZdQHtQECMqPF1SWmc0C7Rdyh4g0pUMO6Bl9T2HCiICWoIg0Unnce2CsqPB3y65a\nGScbKknwUbKKBNj81zkQlyR9IPTjbhzS4AlAkM3iVd/jzvAPEfa8pCIJAQKBgQCB\nc9J6s0vyhczri7AOQgba7djYRnY9iro7IPKJZCow0wLaDyQ6AA9Cv+XqWZ0cuUPN\np9C4cK3Da8lKyMAVH7JYml0LRGh0zHEhlpFqRqwv28wuljMA3Cz+6YSJMVcRI/Ot\nheB8kUjcyLCYCJ1kRdf2k3hY78uz1cmx1TWro882/QKBgBAG9NFVGCorZuZqvmox\nNGOIluK4NRo9g+YX0ElJb3b8vbe9RSVEg63FrrMQJg8TvP2kMllYGCC5RyuLoBjc\nYiClsN7TKzg/IsJiCiYqBlN3YokEQ8ggHYUhcQMC06Fm0ip1qe1wSLGyWDl03UWm\nJl86Wevb5b6ZVoc6ONDG4TMf\n-----END PRIVATE KEY-----\n",
  "client_email": "sheetcrafter@sheetcrafter-316822.iam.gserviceaccount.com",
  "client_id": "106775508412735951836",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheetcrafter%40sheetcrafter-316822.iam.gserviceaccount.com"
}
creds = ServiceAccountCredentials.from_json_keyfile_dict(client_secret,scope)
client = gspread.authorize(creds)
datasheet = ''
ringerboard = ''
ringerboard_specials = ''

specials_masterlist = {}
score_masterlist = {}
pb_masterlist = {}

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
        ringerboard.update(cell,text)
        ringerboard_specials.update(cell, text)
    def get_raw_data(self,timedex):
        master = datasheet.batch_get(["B3:Z5000"])[0]
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
        rnames = ringerboard.batch_get(["A3:B"+rownum],major_dimension='COLUMNS')[0]
        rfirstnames = rnames[1]
        rlastnames = rnames[0]
        rsnames = ringerboard_specials.batch_get(["A3:B"+rownum],major_dimension='COLUMNS')[0]
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
        rownum = sheetnames["Row Number"]
        sp = ringerboard_specials.batch_get(["B3:BE"+rownum])[0]
        ph = []
        for row in sp:
            row = row[1:55]
            ph.append(row)
        return sp
    def get_current_scores(self):
        rownum = sheetnames["Row Number"]
        sc = ringerboard.batch_get(["D3:V"+rownum])[0]
        ph = []
        for row in sc:
            row = row[:18]
            ph.append(row)
        ph = [ph]
        return ph
    def get_current_pb(self):
        rownum = sheetnames["Row Number"]
        pbs = ringerboard_specials.batch_get(["BH1:BH"+rownum])[0]
        pbs = pbs[2:]
        if len(pbs) < (int(rownum)-2):
            for i in range((int(rownum)-2)-len(pbs)):
                pbs.append([])
        return pbs
    def batch_update_ringerboard(self,batch):
        ringerboard.batch_update([batch],value_input_option='USER_ENTERED')
    def batch_update_ringerboard2(self,batch):
        ringerboard_specials.batch_update([batch],value_input_option='USER_ENTERED')
    def batch_update_cells(self,batch,ixs):
        rownum = sheetnames["Row Number"]
        cell_list = ringerboard_specials.range("BH3:BH"+rownum)
        for index,cell in enumerate(cell_list):
            for phdex,rdex in enumerate(ixs):
                if rdex==index: #This cell is cell we want to update
                    cell_list[index].value = batch[phdex]
        ringerboard_specials.update_cells(cell_list,value_input_option='USER_ENTERED')


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
