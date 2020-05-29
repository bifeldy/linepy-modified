# -*- coding: utf-8 -*-

from linepy import *
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pickle, platform
import collections, time, random, sys, json, codecs, threading, glob, os, subprocess, multiprocessing, urllib3, re, ast, requests, tempfile

# Login DateTime (YYYY, MM, DD, hh, mm, ss, ms)
LoginTime = datetime(2013, 8, 27, 1, 12, 23, 345678)

email = None
passw = None

# UserEmail & Password Line Buat Login
try:
    print("-> Line Login!")
    email = os.environ.get('LINE_EMAIL', None)
    passw = os.environ.get('LINE_PASSWORD', None)
    if (email == None and passw == None):
        email = input("Email: ")
        passw = input("Password: ")
    line = LINE(email, passw)
    # line = LINE(token)
    # line = LINE() # Login With QR-Code Link
except Exception as e:
    print(e)
    exit()

line.log("-> Login success! Please wait~ >_<\"")

# Initialize LINE Token
token = line.authToken
line.log("-> Auth Token : " + str(line.authToken))
line.log("-> Timeline Token : " + str(line.tl.channelAccessToken))

# Initialize OEPoll with LINE instance
oepoll = OEPoll(line)

line.log("-> Loading Version Information >_<\"")

Version = {
    'VerMajor':2019,
    'VerMinor':12,
    'VerBuild':10
    }
if os.path.exists('./Version.bin') == True:
    with open("Version.bin", "rb") as pickle_in:
        Version = pickle.load(pickle_in)

Version['VerBuild'] += 1
if Version['VerBuild'] > 9:
    Version['VerMinor'] += 1
    Version['VerBuild'] -= 10
if Version['VerMinor'] > 99:
    Version['VerMajor'] += 1
    Version['VerMinor'] -= 100

with open('Version.bin', 'wb') as pickle_out:
    pickle.dump(Version, pickle_out, pickle.HIGHEST_PROTOCOL)

line.log("-> Loading Profile >_<\"")

# BotStatusNew = line.getProfile()
# BotStatusNew.statusMessage = "-> OnLINE! | v" + str(Version['VerMajor']) + "." + str(Version['VerMinor']) + "." + str(Version['VerBuild'])
# line.updateProfile(BotStatusNew)

line.log("-> Loading Help Messages >_<\"")

helpMessage="""--> Information  <--
1. Semua Perintah Diawali 「!」
2. Masih Ada Beberapa yang Bug~
3. Tidak perlu pakai 「」
4. Langsung Ketik/Tag @Nama"""

helpPublic="""--> Public Commands <--
![About]
![Absen]
![AdminList]
![BlackList]
![BotID]
![CancelInvite ALL]
![CancelInvite 「mid」]
![CheckSR]
![Contact 「@」]
![Contact 「mid」]
![Cover 「@」]
![Cover 「mid」]
![GroupID]
![GroupInfo]
![GroupPict]
![GroupName 「text」]
![HWInfo]
![MyID]
![Pict 「@」]
![Pict 「mid」]
![Ping]
![StaffList]
![Status]
![Status 「@」]
![Status 「mid」]
![ToCreator 「msg」]
![ViewSR]"""

helpStaff="""--> Staff + Admin <--
![AutoCancelInvite ON/OFF]
![AutoCancelURL ON/OFF]
![AutoContactInfo ON/OFF]
![Ban 「@」]
![Ban 「mid」]
![GroupLink ON/OFF]
![GroupURL]
![Invite 「mid」]
![JoinGroupMsg ON/OFF]
![Kick 「@」]
![Kick 「mid」]
![LeaveGroupMsg ON/OFF]
![Protection ON/OFF]
![Staff ADD 「@」]
![Staff ADD 「mid」]
![UnBAN 「@」]
![UnBAN 「mid」]
![UnsentGroupMsg ON/OFF]"""

helpAdmin="""--> Admin Only <--
![Admin ADD 「@」]
![Admin ADD 「mid」]
![Bye]
![CleanGroup]
![Kick BAN]
![Staff REMOVE 「@」]
![Staff REMOVE 「mid」]"""

helpCreator = """--> Creator Only <--
![Add 「@」]
![Add 「mid」]
![Admin REMOVE 「@」]
![Admin REMOVE 「mid」]
![AllowBroadCast 「@」]
![AllowBroadCast 「mid」]
![AutoAdd ON/OFF]
![AutoJoin ON/OFF]
![Balas 「mid」 「msg」]
![BroadCast 「msg」]
![ChangeName 「text」]
![ChangeStatus 「text」]
![JoinGroup 「gid」]
![LeaveGroup 「gid」]
![RejectGroup 「gid」]
![ViewContacts]
![ViewInvitedGroups]
![ViewJoinedGroups]"""

mid = line.getProfile().mid
broadcaster = []

line.log("-> Creating Silent Reader Point >_<\"")

SilentReader = {
    'readPoint':{},
    'readMember':{},
    'setTime':{},
    'ROM':{}
    }

if os.path.exists('./SilentReader.bin') == True:
    with open("SilentReader.bin", "rb") as pickle_in:
        SilentReader = pickle.load(pickle_in)

line.log("-> Preparing Unsend ChatLog >_<\"")

ChatLog = {
    }

if os.path.exists('./ChatLog.bin') == True:
    with open("ChatLog.bin", "rb") as pickle_in:
        ChatLog = pickle.load(pickle_in)

line.log("-> Initializing Admin & Staff Privileges >_<\"")

# Setiap group punya data sendiri - sendiri
Privilege = {
    # Detail UserID Yang Buat~
    'Creator':['u8a43bfe119402c69fe12fb5cdb95b7b3'],
    'Admin':{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:['Admin-UserID1', 'Admin-UserID2']
        # ['GroupID2']:['Admin-UserID1']
        },
    'Staff':{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:['Staff-UserID1']
        # ['GroupID2']:['Staff-UserID1', 'Staff-UserID2']
        },
    'BlackList':{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:['Banned-UserID1']
        # ['GroupID2']:['Banned-UserID1', 'Banned-UserID2']
        }
    }

if os.path.exists('./Privilege.bin') == True:
    with open("Privilege.bin", "rb") as pickle_in:
        Privilege = pickle.load(pickle_in)

line.log("-> Configuring Account Settings >_<\"")

Settings = {
    "Auto_Add":False,
    "AddMe_Msg":True,
    "Auto_JoinGroup":True,
    "Auto_Read":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "Auto_CancelInvite":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "Auto_CancelURL":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "Auto_ContactInfo":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "Group_Protection":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "JoinGroup_Msg":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "LeaveGroup_Msg":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "Unsend_Msg":{
        # Biarin aja kosong ntar ke isi sendiri
        # ['GroupID1']:True
        # ['GroupID2']:False
        },
    "TimeLine":True
    }

if os.path.exists('./Settings.bin') == True:
    with open("Settings.bin", "rb") as pickle_in:
        Settings = pickle.load(pickle_in)

line.log("-> Syncing Line Data >_<\"")

# Initialize Variable # Start
InitGroups = line.getGroupIdsJoined()
for InitGrp in InitGroups:
    InitGInfo = line.getGroup(str(InitGrp))
    if str(InitGrp) not in Privilege['Admin']:
        try:
            gCreatorMid = InitGInfo.creator.mid
            Privilege['Admin'][str(InitGrp)] = []
            Privilege['Admin'][str(InitGrp)].append(str(gCreatorMid))
        except Exception as e:
            print(e)
            Privilege['Admin'][str(InitGrp)] = []
    if str(InitGrp) not in Privilege['Staff']:
        Privilege['Staff'][str(InitGrp)] = []
    if str(InitGrp) not in Privilege['BlackList']:
        Privilege['BlackList'][str(InitGrp)] = []
    if str(InitGrp) not in Settings["Auto_ContactInfo"]:
        Settings["Auto_ContactInfo"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["Auto_CancelInvite"]:
        Settings["Auto_CancelInvite"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["Auto_CancelURL"]:
        Settings["Auto_CancelURL"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["Group_Protection"]:
        Settings["Group_Protection"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["Auto_Read"]:
        Settings["Auto_Read"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["JoinGroup_Msg"]:
        Settings["JoinGroup_Msg"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["LeaveGroup_Msg"]:
        Settings["LeaveGroup_Msg"][str(InitGrp)] = False
    if str(InitGrp) not in Settings["Unsend_Msg"]:
        Settings["Unsend_Msg"][str(InitGrp)] = False
# Save Privilege
with open('Privilege.bin', 'wb') as pickle_out:
    pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
# Save Settings
with open('Settings.bin', 'wb') as pickle_out:
    pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
# Initialize Variable # End

line.log("-> All Done, Ready! Have a nice day~ >_<\"")

# NOTIFIED itu berarti interaksi kita dengan orang lain, bukan orang lain dengan orang lain
# Kalau UserID pake 'mid', Group pake 'gid', RoomID pake 'rid'
# Yang dimaksud 'kita' itu akun ini (BOT-nya)
# Attribut bisa saja Nama, Foto, Status, dll
# https://github.com/cslinmiso/LINE-instant-messenger-protocol/blob/master/line-protocol.md
# Dibawah ini merupakan trigger setelah melakukan sesuatu, bukanperintah untuk melakukan

# Kegiatan selesai # op.type=0
def END_OF_OPERATION(op):
    return

# Kita memperbarui data profil # op.type=1
# op.param1 = Attribut yang di update
def UPDATE_PROFILE(op):
    return

# Orang lain memperbarui data profil # op.type=2
# Cara taunya refresh terus aja looping 'getContact()'
# op.param1 = UserID yang update profil
# op.param2 = Attribut yang di update
def NOTIFIED_UPDATE_PROFILE(op):
    return

# Misteri, Kayanya orang yang baru bikin ID line # op.type=3
def REGISTER_USERID(op):
    return

# Orang lain add orang lain # op.type=4
# Penting banget yak ??
# op.param1 = UserID yang di add
# op.param2 = Misteri, keluarnya angka 0 terus, wkwkwkwk
def ADD_CONTACT(op):
    return

# Ada yang nge-add kita # op.type=5
# op.param1 = UserID Yang nge-add kita
def NOTIFIED_ADD_CONTACT(op):
    line.log("[NOTIFIED_ADD_CONTACT] [%s]" % (line.getContact(op.param1).displayName))
    try:
        try:
            if Settings["Auto_Add"] == True:
                line.findAndAddContactsByMid(op.param1) # Auto-Add User~
        except Exception as e:
            print(e)
            pass
        if Settings["AddMe_Msg"] == True:
            line.sendMessage(op.param1, "Hi " + line.getContact(op.param1).displayName + "~\nSalam kenal.\nHehe >_<\"\n\nThanks for adding me-\nAs friend~")
            statusSticker = ['15263','15264']
            line.sendSticker(op.param1, '966', random.choice(statusSticker))
    except Exception as e:
        line.log("[NOTIFIED_ADD_CONTACT] ERROR : " + str(e))
    return

# Kita nge-block kontak # op.type=6
# op.param1 = UserID yang kita block
# op.param2 = Misteri, keluarnya op.message.text 'NORMAL', wkwkwk
def BLOCK_CONTACT(op):
    return

# Kita nge-unblock kontak # op.type=7
# op.param1 = UserID yang kita unblock
# op.param2 = Misteri, keluarnya op.message.text 'NORMAL', wkwkwk
def UNBLOCK_CONTACT(op):
    return

# Kita buat group # op.type=9
def CREATE_GROUP(op):
    return

# Kita update data group (kita dalam group) # op.type=10
# op.param1 = GroupID
# op.param2 = Attribut yang di update
def UPDATE_GROUP(op):
    return
    
# Orang lain update data group (kita dalam group) # op.type=11
# op.param1 = GroupID
# op.param2 = UserID yang update
# op.param3 = Attribut yang di update
def NOTIFIED_UPDATE_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[NOTIFIED_UPDATE_GROUP] [%s] [%s]" % (ginfo.name, line.getContact(op.param2).displayName))
    try:
        if Settings["Auto_CancelURL"][str(op.param1)] == True:
            if line.getGroup(op.param1).preventedJoinByTicket == False:
                if op.param2 in Privilege['Staff'][str(op.param1)]:
                    pass
                if op.param2 in Privilege['Admin'][str(op.param1)]:
                    pass
                if op.param2 in Privilege['Creator']:
                    pass
                else:
                    line.sendMessage(op.param1, "URL-nya jangan di buka ..\nNanti ada kicker masuk~\nBahaya ..\nLalala~ (T_T\")")
                    line.kickoutFromGroup(op.param1,[op.param2])
                    Privilege['BlackList'][str(op.param1)].append(str(op.param2))
                    line.sendMessage(op.param1, "URL dibuka paksa ..\nAdded to blacklist.\nAuto kicked~ (T_T\")")
                    line.reissueGroupTicket(op.param1)
                    X = line.getGroup(op.param1)
                    X.preventedJoinByTicket = True
                    line.updateGroup(X)
                    with open('Privilege.bin', 'wb') as pickle_out:
                        pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        line.log("[AUTO_CANCEL_GROUP_URL] ERROR : " + str(e))
    return

# Kita invite orang lain ke group (kita dalam group) # op.type=12
# op.param1 = GroupID
# op.param2 = UserID yang kita invite
def INVITE_INTO_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[INVITE_INTO_GROUP] [%s] [%s]" % (ginfo.name, line.getContact(op.param2).displayName))
    try:
        if op.param2 in Privilege['BlackList'][str(op.param1)]:
            Privilege['BlackList'][str(op.param1)].remove(str(op.param3))
            with open('Privilege.bin', 'wb') as pickle_out:
                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        line.log("[AUTO_CANCEL_GROUP_URL] ERROR : " + str(e))
    return

# Ada invite ke group # op.type=13
# op.param1 = GroupID
# op.param2 = UserID yang nge-invite
# op.param3 = UserID yang di-invite
def NOTIFIED_INVITE_INTO_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[NOTIFIED_INVITE_INTO_GROUP] [%s] [%s->%s]" % (ginfo.name, line.getContact(op.param2).displayName, line.getContact(op.param3).displayName))
    try:
        if op.param3 == mid:
            if Settings["Auto_JoinGroup"] == True:
                try:
                    line.acceptGroupInvitation(op.param1)
                except Exception as e:
                    print(e)
        else:
            if op.param2 in Privilege['Staff'][str(op.param1)] or op.param2 in Privilege['Admin'][str(op.param1)] or op.param2 in Privilege['Creator']:
                if op.param3 in Privilege['BlackList'][str(op.param1)]:
                    Privilege['BlackList'][str(op.param1)].remove(str(op.param3))
                    with open('Privilege.bin', 'wb') as pickle_out:
                        pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
            if Settings["Auto_CancelInvite"][str(op.param1)] == True:
                try:
                    X = line.getGroup(op.param1)
                    gInviMids = [contact.mid for contact in X.invitee]
                    line.cancelGroupInvitation(op.param1, gInviMids)
                except Exception as e:
                    print(e)
                    try:
                        X = line.getGroup(op.param1)
                        gInviMids = [contact.mid for contact in X.invitee]
                        line.cancelGroupInvitation(op.param1, gInviMids)
                    except Exception as e:
                        line.log("[NOTIFIED_INVITE_INTO_GROUP] ERROR : " + str(e))
                line.sendMessage(op.param1, "Hati-hati kalo nge-Invite~\nNtar ada kicker~ >_<\"")
                return
    except Exception as e:
        line.log("[NOTIFIED_INVITE_INTO_GROUP] ERROR : " + str(e))
    return

# Kita keluar group  # op.type=14
# op.param1 = GroupID
def LEAVE_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[LEAVE_GROUP] [%s]" % (ginfo.name))
    Privilege['Admin'].pop(str(op.param1), 0)
    Privilege['Staff'].pop(str(op.param1), 0)
    Privilege['BlackList'].pop(str(op.param1), 0)
    Settings["Auto_ContactInfo"].pop(str(op.param1), 0)
    Settings["Auto_CancelInvite"].pop(str(op.param1), 0)
    Settings["Auto_Read"].pop(str(op.param1), 0)
    Settings["Auto_CancelURL"].pop(str(op.param1), 0)
    Settings["Group_Protection"].pop(str(op.param1), 0)
    Settings["JoinGroup_Msg"].pop(str(op.param1), 0)
    Settings["LeaveGroup_Msg"].pop(str(op.param1), 0)
    Settings["Unsend_Msg"].pop(str(op.param1), 0)
    with open('Privilege.bin', 'wb') as pickle_out:
        pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
    with open('Settings.bin', 'wb') as pickle_out:
        pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
    return

# Ada orang lain yang left dari group (kita dalam group) # op.type=15
# op.param1 = GroupID
# op.param2 = UserID yang left
def NOTIFIED_LEAVE_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[NOTIFIED_LEAVE_GROUP] [%s] [%s]" % (ginfo.name, line.getContact(op.param2).displayName))
    try:
        if Settings["LeaveGroup_Msg"][str(op.param1)] == True:
            line.sendMessage(op.param1, "Selamat Tinggal~\n" + line.getContact(op.param2).displayName + "\nHmn~ (~_~メ)")
    except Exception as e:
        line.log("[NOTIFIED_LEAVE_GROUP] ERROR : " + str(e))
    return

# Kita nerima invite-an group terus masuk # op.type=16
# op.param1 = GroupID
def ACCEPT_GROUP_INVITATION(op):
    ginfo = line.getGroup(op.param1)
    line.log("[ACCEPT_GROUP_INVITATION] [%s]" % (ginfo.name))
    try:
        gCreatorMid = ginfo.creator.mid
        Privilege['Admin'][str(op.param1)] = []
        Privilege['Admin'][str(op.param1)].append(str(gCreatorMid))
    except Exception as e:
        print(e)
        Privilege['Admin'][str(op.param1)] = []
    Privilege['Staff'][str(op.param1)] = []
    Privilege['BlackList'][str(op.param1)] = []
    Settings["Auto_Read"][str(op.param1)] = True
    Settings["Auto_ContactInfo"][str(op.param1)] = True
    Settings["Auto_CancelInvite"][str(op.param1)] = False
    Settings["Auto_CancelURL"][str(op.param1)] = False
    Settings["Group_Protection"][str(op.param1)] = False
    Settings["JoinGroup_Msg"][str(op.param1)] = True
    Settings["LeaveGroup_Msg"][str(op.param1)] = False
    Settings["Unsend_Msg"][str(op.param1)] = True
    with open('Privilege.bin', 'wb') as pickle_out:
        pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
    with open('Settings.bin', 'wb') as pickle_out:
        pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
    line.sendMessage(op.param1, "Hai Semua..\nSalam Kenal~\n(｡>﹏<｡)\"\n\nType !help for more info.")
    return

# Ada orang lain join group juga (kita dalam group) # op.type=17
# op.param1 = GroupID
# op.param2 = UserID yang join
def NOTIFIED_ACCEPT_GROUP_INVITATION(op):
    ginfo = line.getGroup(op.param1)
    line.log("[NOTIFIED_ACCEPT_GROUP_INVITATION] [%s] [%s]" % (ginfo.name, line.getContact(op.param2).displayName))
    try:
        if op.param2 in Privilege['BlackList'][str(op.param1)]: # Yang ke blacklist Auto Kick
            line.sendMessage(op.param1, line.getContact(op.param2).displayName + " ada didalam daftar hitam atas keinginan admin / staff.")
            line.sendMessage(op.param2, "Hai~ " + line.getContact(op.param2).displayName + "\nKamu tidak dapat bergabung ke dalam group " + ginfo.name + " dikarenakan kamu ada didalam daftar hitam atas keinginan admin / staff.")
            line.kickoutFromGroup(op.param1,[op.param2])
            try:
                for LoopStaff in Privilege['Staff'][str(op.param1)]:
                    line.sendContact(op.param2, LoopStaff)
            except Exception as e:
                print(e)
                pass
            try:
                for LoopAdmin in Privilege['Admin'][str(op.param1)]:
                    line.sendContact(op.param2, LoopAdmin)
            except Exception as e:
                print(e)
                pass
            line.sendMessage(op.param2, "Silahkan menghubungi kontak admin / staff di atas.")
        else:
            if Settings["JoinGroup_Msg"][str(op.param1)] == True:
                joinMsg = ["Selamat Datang~ [list] \nHave fun~ (^_^メ)", "Hai~ [list] \nSalam Kenal~ (>_<)", "Welcome~ [list] \nHave A Nice Day~ (O.o\")"]
                line.sendMessageWithMention(op.param1, random.choice(joinMsg), [op.param2])
    except Exception as e:
        line.log("[NOTIFIED_ACCEPT_GROUP_INVITATION] ERROR : " + str(e))
    return

# Kita nge-kick orang dari group # op.type=18
# op.param1 = GroupID
# op.param2 = UserID yang di-kick
def KICKOUT_FROM_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[KICKOUT_FROM_GROUP] [%s] [%s]" % (ginfo.name, line.getContact(op.param2).displayName))
    try:
        line.sendMessage(op.param1, "Bye Bye~\n" + line.getContact(op.param2).displayName + "\n(>_<\")")
    except Exception as e:
        line.log("[KICKOUT_FROM_GROUP] ERROR : " + str(e))
    return
        
# Orang lain nge-kick orang lain # op.type=19
# op.param1 = GroupID
# op.param2 = UserID yang nge-kick
# op.param3 = UserId yang di-Kick
def NOTIFIED_KICKOUT_FROM_GROUP(op):
    ginfo = line.getGroup(op.param1)
    line.log("[NOTIFIED_UPDATE_GROUP] [%s] [%s->%s]" % (ginfo.name, line.getContact(op.param2).displayName, line.getContact(op.param3).displayName))
    try:
        if Settings["Group_Protection"][str(op.param1)] == True:
            if op.param2 in Privilege['Staff'][str(op.param1)] or op.param2 in Privilege['Admin'][str(op.param1)] or op.param2 in Privilege['Creator']:
                pass
            else:
                line.sendMessage(op.param1, "Jangan nge-kick sembarangan~\nAuto kick executed.")
                line.kickoutFromGroup(op.param1,[op.param2])
                try:
                    line.findAndAddContactsByMid(op.param3) # Auto-Add Kicked User~
                except Exception as e:
                    print(e)
                    pass
                line.inviteIntoGroup(op.param1,[op.param3])
                Privilege['BlackList'][str(op.param1)].append(str(op.param2))
                with open('Privilege.bin', 'wb') as pickle_out:
                    pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        line.log("[AUTO_CANCEL_GROUP_URL] ERROR : " + str(e))
    return

# Kita buat room chat (multichat) # op.type=20
# op.param1 = RoomID
def CREATE_ROOM(op):
    return

# Kita invite orang lain (bisa banyak) ke dalam room # op.type=21
# op.param1 = RoomID
# op.param2 = [UserID] yang di invite (bisa banyak)
def INVITE_INTO_ROOM(op):
    return

# Kita di invite ke multichat (udah auto join pastinya) # op.type=22
# op.param1 = RoomID
# op.param2 = UserID yang nge-invite kita
# op.param3 = UserID orang lain yang ada di multichat (bisa banyak)
def NOTIFIED_INVITE_INTO_ROOM(op):
    return

# Kita keluar room chat # op.type=23
# op.param1 = RoomID
def LEAVE_ROOM(op):
    return

# Ada orang lain yang keluar dari room char # op.type=24
# op.param1 = RoomID
# op.param2 = UserID yang left
def NOTIFIED_LEAVE_ROOM(op):
    return

# Chat Bot # in-Group Only
# op.message.toType = 0 => Private Chat
# op.message.toType = 2 => Group Chat
# op.message.contentType = 0 => Text
# op.message.contentType = 1 => Photo
# op.message.contentType = 2 => Video
# op.message.contentType = 3 => Voice Chat
# op.message.contentType = 6 => Video / Voice Call
# op.message.contentType = 7 => Sticker
# op.message.contentType = 13 => Line Contact
# op.message.contentType = 14 => Files
# op.message.contentType = 16 => Create Notes / Albums
# op.message.contentType = 18 => Delete Notes / Albums
# op.message._from = UserID pengirim pesan di group
# op.message.to = GroupID
def BOT_COMMANDS(op, ginfo):
    start = time.time()
    contact = line.getContact(op.message._from) # Get sender contact
    if Settings["Auto_Read"][str(op.message.to)] == True:
        line.sendChatChecked(op.message.to, op.message.id) # Buat ilangin notif di HP
    # Content Message # Multimedia
    if op.message.contentType == 13:
        if Settings["Auto_ContactInfo"][str(op.message.to)] == True:
            # op.message.contentType = 0
            contacts = line.getContact(op.message.contentMetadata["mid"])
            try:
                cu = line.getProfileCoverURL(op.message.contentMetadata["mid"])
            except Exception as e:
                print(e)
                cu = "Line API Error."
            try:
                AccTimeStamp = contacts.createdTime
                AccTime = datetime.fromtimestamp(AccTimeStamp/1e3)
                createdTime = AccTime.strftime('%Y-%m-%d @ %H:%M:%S.%f')
            except Exception as e:
                print(e)
                createdTime = "Error - Joined Since LINE BetA!"
            line.sendMessage(op.message.to,"[displayName]\n" + contacts.displayName + "\n\n[mID]\n" + op.message.contentMetadata["mid"] + "\n\n[createdTime]\n" + createdTime + "\n\n[statusMessage]\n" + contacts.statusMessage + "\n\n[pictureStatus]\nhttp://dl.profile.line-cdn.net/" + contacts.pictureStatus + "\n\n[coverURL]\n" + str(cu))
    # Content Message # op.message.text Only
    if op.message.contentType == 0:
        if op.message.toType == 2:
            if op.message.text is None:
                return
            # line.log('[%s] [%s] %s' % (ginfo.name, line.getContact(op.message._from).displayName, op.message.text))
            # Everyone inside group only op.message.text Command list # Start
            if op.message.text.lower() == '!about':
                try:
                    for LoopCreator in Privilege['Creator']:
                        line.sendContact(op.message.to, LoopCreator)
                except Exception as e:
                    print(e)
                    pass
                diff = relativedelta(datetime.now(), LoginTime)
                line.sendMessage(op.message.to, 'Main Creator: \"B. Bias A. Ch.\"\n\nSDK: Python%s\nCompiler: %s\nBuild Ver: %s\nBuild Date: %s\n\nMore info :\nline://ti/p/~Bifeldy (^ム^)\n\nUpTime:\n%d years %d months %d days\n%d hours %d minutes %d seconds' % (platform.python_version(), platform.python_compiler(), platform.python_build()[0], platform.python_build()[1], diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds))
                statusSticker = ['15263','15264','15265','15266','15267','15268','15269','15270']
                line.sendSticker(op.message.to, '966', random.choice(statusSticker))
            elif op.message.text.lower() == '!gift':
                line.sendMessage(op.message.to, '', None, 9)
            elif op.message.text.lower() == "!groupid":
                line.sendMessage(op.message.to, "This GroupID :\n%s" % (op.message.to))
            elif op.message.text.lower() == "!botid":
                line.sendMessage(op.message.to, "My MemberID :\n%s" % (mid))
            elif op.message.text.lower() == "!myid":
                line.sendMessage(op.message.to, "Your MemberID :\n%s" % (op.message._from))
            elif op.message.text.lower() == "!ping":
                line.sendMessage(op.message.to, "%.2f ms." % ((time.time() - start)*1000))
            elif '!status @' in op.message.text.lower():
                try:
                    key = eval(op.message.contentMetadata["MENTION"])
                    mmid = key["MENTIONEES"][0]["M"]
                    contacts = line.getContact(mmid)
                    try:
                        cu = line.getProfileCoverURL(mmid)
                    except Exception as e:
                        print(e)
                        cu = "Line API Error."
                    try:
                        createdTime = datetime.fromtimestamp((contacts.createdTime)/1e3).strftime('%A, %d %B %Y @ %H:%M:%S.%f (%p)')
                    except Exception as e:
                        print(e)
                        createdTime = "Error - Joined Since LINE BetA!"
                    line.sendMessageWithMention(op.message.to,"[displayName] [list] \n\n[mID]\n" + op.message.contentMetadata["mid"] + "\n\n[createdTime]\n" + createdTime + "\n\n[statusMessage]\n" + contacts.statusMessage + "\n\n[pictureStatus]\nhttp://dl.profile.line-cdn.net/" + contacts.pictureStatus + "\n\n[coverURL]\n" + str(cu), [mmid])
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif '!status ' in op.message.text.lower():
                try:
                    mmid = op.message.text[8:]
                    contacts = line.getContact(mmid)
                    try:
                        cu = line.getProfileCoverURL(mmid)
                    except Exception as e:
                        print(e)
                        cu = "Line API Error."
                    try:
                        createdTime = datetime.fromtimestamp((contacts.createdTime)/1e3).strftime('%A, %d %B %Y @ %H:%M:%S.%f (%p)')
                    except Exception as e:
                        print(e)
                        createdTime = "Error - Joined Since LINE BetA!"
                    line.sendMessage(op.message.to,"[displayName]\n" + contacts.displayName + "\n\n[mID]\n" + mmid + "\n\n[createdTime]\n" + createdTime + "\n\n[statusMessage]\n" + contacts.statusMessage + "\n\n[pictureStatus]\nhttp://dl.profile.line-cdn.net/" + contacts.pictureStatus + "\n\n[coverURL]\n" + str(cu))
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif op.message.text.lower() == "!cancelinvite all":
                X = line.getGroup(op.message.to)
                line.sendMessage(op.message.to,"Canceling all pending(s) invitation.")
                if X.invitee is not None:
                    gInviMids = [contact.mid for contact in X.invitee]
                    line.cancelGroupInvitation(op.message.to, gInviMids)
                else:
                    line.sendMessage(op.message.to,"This group doesn't have any pending invitation.")
            elif "!cancelinvite " in op.message.text.lower():
                try:
                    targets = op.message.text[14:]
                    line.sendMessage(op.message.to,"Canceling %s invitation." % (line.getContact(targets).displayName))
                    line.cancelGroupInvitation(op.message.to, targets)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found or not yet invited.")
            elif '!contact @' in op.message.text.lower():
                try:
                    key = eval(op.message.contentMetadata["MENTION"])
                    mmid = key["MENTIONEES"][0]["M"]
                    line.sendContact(op.message.to, mmid)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif '!contact ' in op.message.text.lower():
                try:
                    mmid = op.message.text[9:]
                    line.sendContact(op.message.to, mmid)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif op.message.text.lower() == '!grouppict':
                line.sendImageWithURL(op.message.to, 'http://dl.profile.line.naver.jp/'+ginfo.pictureStatus)
            elif '!pict @' in op.message.text.lower():
                try:
                    key = eval(op.message.contentMetadata["MENTION"])
                    mmid = key["MENTIONEES"][0]["M"]
                    line.sendImageWithURL(op.message.to, 'http://dl.profile.line.naver.jp/'+line.getContact(mmid).pictureStatus)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif '!pict ' in op.message.text.lower():
                try:
                    mmid = op.message.text[6:]
                    line.sendImageWithURL(op.message.to, 'http://dl.profile.line.naver.jp/'+line.getContact(mmid).pictureStatus)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif '!cover @' in op.message.text.lower():
                try:
                    key = eval(op.message.contentMetadata["MENTION"])
                    mmid = key["MENTIONEES"][0]["M"]
                    line.sendImageWithURL(op.message.to, line.getProfileCoverURL(mmid))
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif '!cover ' in op.message.text.lower():
                try:
                    mmid = op.message.text[7:]
                    line.sendImageWithURL(op.message.to, line.getProfileCoverURL(mmid))
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found.")
                    return
            elif op.message.text.lower() in ['!blacklist', '!banlist']:
                if Privilege['BlackList'][str(op.message.to)] == []:
                    line.sendMessage(op.message.to,"No users is blacklist.")
                else:
                    mc = "Blacklist:"
                    for mi_d in Privilege['BlackList'][str(op.message.to)]:
                        mc += "\n- " +line.getContact(mi_d).displayName
                    line.sendMessage(op.message.to,mc)
            elif op.message.text.lower() == "!absen":
                line.sendMessage(op.message.to, "Hadir >_<\"")
            elif op.message.text.lower() == "!stafflist":
                if op.message.to in Privilege['Staff']:
                    if Privilege['Staff'][str(op.message.to)] == []:
                        line.sendMessage(op.message.to,"The StaffList is empty.")
                    else:
                        mc = "Staff list:"
                        for mi_d in Privilege['Staff'][str(op.message.to)]:
                            mc += "\n-> " +line.getContact(mi_d).displayName
                        line.sendMessage(op.message.to,mc)
                else:
                    line.sendMessage(op.message.to,"The AdminList is empty.")
            elif op.message.text.lower() == "!adminlist":
                if op.message.to in Privilege['Admin']:
                    if Privilege['Admin'][str(op.message.to)] == []:
                        line.sendMessage(op.message.to,"The AdminList is empty.")
                    else:
                        mc = "Admin list:"
                        for mi_d in Privilege['Admin'][str(op.message.to)]:
                            mc += "\n-> " +line.getContact(mi_d).displayName
                        line.sendMessage(op.message.to,mc)
                else:
                    line.sendMessage(op.message.to,"The AdminList is empty.")
            elif op.message.text.lower() == "!groupinfo":
                try:
                    gCreator = ginfo.creator.displayName
                except Exception as e:
                    print(e)
                    gCreator = "Error - Unknown!"
                if ginfo.invitee is None:
                    sinvitee = "0"
                else:
                    sinvitee = str(len(ginfo.invitee))
                if ginfo.preventedJoinByTicket == True:
                    u = "Closed."
                else:
                    u = "Opened."
                try:
                    createdTime = datetime.fromtimestamp((ginfo.createdTime)/1e3).strftime('%A, %d %B %Y @ %H:%M:%S.%f (%p)')
                except Exception as e:
                    print(e)
                    createdTime = "Error - Created Since LINE BetA!"
                line.sendMessage(op.message.to,"[groupName]\n" + ginfo.name + "\n\n[gID]\n" + ginfo.id + "\n\n[createdTime]\n" + createdTime + "\n\n[groupCreator]\n" + gCreator + "\n\n[groupPicture]\nhttp://dl.profile.line.naver.jp/" + ginfo.pictureStatus + "\n\nInvite Pending: " + sinvitee + "\nURL/QR-Link: " + u)
            elif op.message.text.lower() == "!hwinfo":
                line.sendMessage(op.message.to, "System: " + platform.system() + "\nVersion: " + platform.version() + "\nProcessor: " + platform.processor())
            elif "!groupname " in op.message.text.lower():
                X = line.getGroup(op.message.to)
                try:
                    X.name = op.message.text[11:]
                    line.updateGroup(X)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"GroupName should 1-20 Chars!.")
                    return
            elif op.message.text.lower() == "!checksr":
                line.sendMessage(op.message.to, "Checked~")
                try:
                    del SilentReader['readPoint'][str(op.message.to)]
                    del SilentReader['readMember'][str(op.message.to)]
                except Exception as e:
                    print(e)
                    pass
                SilentReader['readPoint'][str(op.message.to)] = op.message.id
                SilentReader['readMember'][str(op.message.to)] = ""
                SilentReader['setTime'][str(op.message.to)] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " JST+9"
                SilentReader['ROM'][str(op.message.to)] = {}
            elif op.message.text.lower() == "!viewsr":
                if op.message.to in SilentReader['readPoint']:
                    if SilentReader["ROM"][str(op.message.to)].items() == []:
                        chiya = ""
                    else:
                        chiya = ""
                        for rom in SilentReader["ROM"][str(op.message.to)].items():
                            chiya += rom[1] + "\n"
                    line.sendMessage(op.message.to, "Readers:\n%s\nLast checked:\n[%s]"  % (chiya, SilentReader['setTime'][str(op.message.to)]))
                else:
                    line.sendMessage(op.message.to, "No check-point.\nType !「CheckSR」 first~")
            elif op.message.text.lower() == "!status":
                diff = relativedelta(datetime.now(), LoginTime)
                ping = (time.time() - start)
                line.sendMessage(op.message.to, "%s Status\nGroup: %s\n\n-> Auto_CancelInvite: %s\n-> Auto_CancelURL: %s\n-> Auto_ContactInfo: %s\n-> Group_Protection: %s\n-> JoinGroup_Msg: %s\n-> LeaveGroup_Msg: %s\n-> Unsend_Msg: %s\n\n-> Server: %s\n# Hehehe >_<\"\n\nUpTime:\n%d years %d months %d days\n%d hours %d minutes %d seconds" % ((line.getContact(mid).displayName), ginfo.name, ('Yes.' if Settings["Auto_CancelInvite"][op.message.to] == True else 'No.'), ('Yes.' if Settings["Auto_CancelURL"][op.message.to] == True else 'No.'), ('Yes.' if Settings["Auto_ContactInfo"][op.message.to] == True else 'No.'), ('Yes.' if Settings["Group_Protection"][op.message.to] == True else 'No.'), ('Yes.' if Settings["JoinGroup_Msg"][op.message.to] == True else 'No.'), ('Yes.' if Settings["LeaveGroup_Msg"][op.message.to] == True else 'No.'), ('Yes.' if Settings["Unsend_Msg"][op.message.to] == True else 'No.'), ('Normal Load.' if ping <= 0.5 else ('Heavy Load.' if ping <= 1.0 else 'Full Load.')), diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds))
                statusSticker = ['15263','15264','15265','15266','15267','15268','15269','15270']
                line.sendSticker(op.message.to, '966', random.choice(statusSticker))
            elif op.message.text.lower() == '!help':
                line.sendMessage(op.message.to, "Message sent, Check Private Message~\nIf not, add me first~")
                line.sendMessage(op.message._from, "--> Help <--\n# Name: %s\n# Group: %s\n# Role: %s" % (contact.displayName, ginfo.name, ('Creator.' if op.message._from in Privilege["Creator"] else ('Admin.' if op.message._from in Privilege["Admin"][str(op.message.to)] else ('Staff.' if op.message._from in Privilege["Staff"][str(op.message.to)] else ('Member.'))))))
                line.sendMessage(op.message._from, helpMessage)
                line.sendMessage(op.message._from, helpPublic)
                if op.message._from in Privilege['Creator']:
                    line.sendMessage(op.message._from, helpStaff)
                    line.sendMessage(op.message._from, helpAdmin)
                    line.sendMessage(op.message._from, helpCreator)
                elif op.message._from in Privilege['Admin'][str(op.message.to)]:
                    line.sendMessage(op.message._from, helpStaff)
                    line.sendMessage(op.message._from, helpAdmin)
                elif op.message._from in Privilege['Staff'][str(op.message.to)]:
                    line.sendMessage(op.message._from, helpStaff)
            elif '!tocreator ' in op.message.text.lower():
                for MsgToCrt in Privilege['Creator']:
                    if MsgToCrt == mid:
                        pass
                    else:
                        line.sendMessage(MsgToCrt, "From: " + contact.displayName + "\n\nmID: " + op.message._from + "\n\nGroup: " + ginfo.name + "\n\ngID: " + op.message.to + "\n\nMessages: \n" + op.message.text[11:])
            # Everyone inside group only op.message.text Command list # End
            #---#
            # Staff inside group only op.message.text Command list # Start
            elif "!staff add @" in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if targets in Privilege['Creator']:
                        line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                    elif targets in Privilege['Admin'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"It's admin, Higher than Staff.")
                    elif targets in Privilege['Staff'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Already a staff.")
                    else:
                        Privilege['Staff'][str(op.message.to)].append(targets)
                        line.sendMessage(op.message.to,"Promoted as a Staff~")
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif "!staff add " in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[11:]
                        if targets in Privilege['Creator']:
                            line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                        elif targets in Privilege['Admin'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"It's admin, Higher than Staff.")
                        elif targets in Privilege['Staff'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Already a staff.")
                        else:
                            Privilege['Staff'][str(op.message.to)].append(targets)
                            line.sendMessage(op.message.to,"Promoted as a Staff~")
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif "!kick @" in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if mmid in Privilege['Staff'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Can't kick staff~.")
                    elif mmid in Privilege['Admin'][str(op.message.to)] or mmid in Privilege['Creator']:
                        line.sendMessage(op.message.to,"Can't kick admin~.")
                    else:
                        line.kickoutFromGroup(op.message.to,[mmid])
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif "!kick " in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        mmid = op.message.text[6:]
                        if mmid in Privilege['Staff'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Can't kick staff~.")
                        elif mmid in Privilege['Admin'][str(op.message.to)] or mmid in Privilege['Creator']:
                            line.sendMessage(op.message.to,"Can't kick admin~.")
                        else:
                            line.kickoutFromGroup(op.message.to,[mmid])
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!grouplink off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    X = line.getGroup(op.message.to)
                    if X.preventedJoinByTicket == False:
                        X.preventedJoinByTicket = True
                        line.updateGroup(X)
                        line.sendMessage(op.message.to,"Invitation link turned OFF.")
                    else:
                        line.sendMessage(op.message.to,"Already turned OFF.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!grouplink on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    X = line.getGroup(op.message.to)
                    if X.preventedJoinByTicket == True:
                        X.preventedJoinByTicket = False
                        line.updateGroup(X)
                        line.sendMessage(op.message.to,"Invitation link turned ON.")
                    else:
                        line.sendMessage(op.message.to,"Already turned ON.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!groupurl":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    x = line.getGroup(op.message.to)
                    if x.preventedJoinByTicket == True:
                        x.preventedJoinByTicket = False
                        line.updateGroup(x)
                    gurl = line.reissueGroupTicket(op.message.to)
                    line.sendMessage(op.message.to,"line://ti/g/" + gurl)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif "!ban @" in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if targets in Privilege['BlackList'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Already.")
                    elif targets in Privilege['Staff'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Can't ban staff.")
                    elif targets in Privilege['Admin'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Can't ban admin.")
                    elif targets in Privilege['Creator']:
                        line.sendMessage(op.message.to,"Can't ban creator.")
                    else:
                        Privilege['BlackList'][str(op.message.to)].append(targets)
                        line.sendMessage(op.message.to,"Added to blacklist.")
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif '!ban ' in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[5:]
                        if targets in Privilege['BlackList'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Already.")
                        elif targets in Privilege['Staff'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Can't ban staff.")
                        elif targets in Privilege['Admin'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Can't ban admin.")
                        elif targets in Privilege['Creator']:
                            line.sendMessage(op.message.to,"Can't ban creator.")
                        else:
                            Privilege['BlackList'][str(op.message.to)].append(targets)
                            line.sendMessage(op.message.to,"Added to blacklist.")
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif "!unban @" in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if targets in Privilege['Staff'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Staff always whitelist.")
                    elif targets in Privilege['Admin'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Admin always whitelist.")
                    elif targets in Privilege['Creator']:
                        line.sendMessage(op.message.to,"Creator always whitelist.")
                    elif targets in Privilege['BlackList'][str(op.message.to)]:
                        Privilege['BlackList'][str(op.message.to)].remove(targets)
                        line.sendMessage(op.message.to,"Removed from blacklist.")
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to,"Already.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif '!unban ' in op.message.text.lower():
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[7:]
                        if targets in Privilege['Staff'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Staff always whitelist.")
                        elif targets in Privilege['Admin'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Admin always whitelist.")
                        elif targets in Privilege['Creator']:
                            line.sendMessage(op.message.to,"Creator always whitelist.")
                        elif targets in Privilege['BlackList'][str(op.message.to)]:
                            Privilege['BlackList'][str(op.message.to)].remove(targets)
                            line.sendMessage(op.message.to,"Removed from blacklist.")
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                        else:
                            line.sendMessage(op.message.to,"Already.")
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif "!invite " in op.message.text.lower():
                targets = op.message.text[8:]
                try:
                    line.inviteIntoGroup(op.message.to,[targets])
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message.to,"Contact not found or not yet added as friend. Try ![Add 「mid」] first~")
            elif op.message.text.lower() == "!autocancelinvite off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_CancelInvite"][str(op.message.to)] == True:
                        Settings["Auto_CancelInvite"][str(op.message.to)] = False
                        line.sendMessage(op.message.to, "AutoCancelInvite turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "AutoCancelInvite already turned OFF")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autocancelinvite on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_CancelInvite"][str(op.message.to)] == False:
                        Settings["Auto_CancelInvite"][str(op.message.to)] = True
                        line.sendMessage(op.message.to, "AutoCancelInvite turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "AutoCancelInvite already turned ON.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autoread off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_Read"][str(op.message.to)] == True:
                        Settings["Auto_Read"][str(op.message.to)] = False
                        line.sendMessage(op.message.to, "Auto_Read turned OFF")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "Auto_Read already turned OFF.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autoread on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_Read"][str(op.message.to)] == False:
                        Settings["Auto_Read"][str(op.message.to)] = True
                        line.sendMessage(op.message.to, "Auto_Read turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "Auto_Read already turned ON.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autocancelurl off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_CancelURL"][str(op.message.to)] == True:
                        Settings["Auto_CancelURL"][str(op.message.to)] = False
                        line.sendMessage(op.message.to, "AutoCancelURL turned OFF")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "AutoCancelURL already turned OFF.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autocancelurl on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_CancelURL"][str(op.message.to)] == False:
                        Settings["Auto_CancelURL"][str(op.message.to)] = True
                        line.sendMessage(op.message.to, "AutoCancelURL turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "AutoCancelURL already turned ON.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!protection on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Group_Protection"][str(op.message.to)] == False:
                        Settings["Group_Protection"][str(op.message.to)] = True
                        line.sendMessage(op.message.to, "Protection turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "Protection already ON.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!protection off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Group_Protection"][str(op.message.to)] == True:
                        Settings["Group_Protection"][str(op.message.to)] = False
                        line.sendMessage(op.message.to, "Protection turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "Protection already OFF.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autocontactinfo on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_ContactInfo"][str(op.message.to)] == False:
                        Settings["Auto_ContactInfo"][str(op.message.to)] = True
                        line.sendMessage(op.message.to, "ContactInfo turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "ContactInfo already ON.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!autocontactinfo off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Auto_ContactInfo"][str(op.message.to)] == True:
                        Settings["Auto_ContactInfo"][str(op.message.to)] = False
                        line.sendMessage(op.message.to, "ContactInfo turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to, "ContactInfo already OFF.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!joingroupmsg on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["JoinGroup_Msg"][str(op.message.to)] == True:
                        line.sendMessage(op.message.to,"JoinGroupMessage already ON.")
                    else:
                        Settings["JoinGroup_Msg"][str(op.message.to)] = True
                        line.sendMessage(op.message.to,"JoinGroupMessage turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!joingroupmsg off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["JoinGroup_Msg"][str(op.message.to)] == False:
                        line.sendMessage(op.message.to,"JoinGroupMessage already OFF.")
                    else:
                        Settings["JoinGroup_Msg"][str(op.message.to)] = False
                        line.sendMessage(op.message.to,"JoinGroupMessage turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!leavegroupmsg on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["LeaveGroup_Msg"][str(op.message.to)] == True:
                        line.sendMessage(op.message.to,"LeaveGroupMessage already ON.")
                    else:
                        Settings["LeaveGroup_Msg"][str(op.message.to)] = True
                        line.sendMessage(op.message.to,"LeaveGroupMessage turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!leavegroupmsg off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["LeaveGroup_Msg"][str(op.message.to)] == False:
                        line.sendMessage(op.message.to,"LeaveGroupMessage already OFF.")
                    else:
                        Settings["LeaveGroup_Msg"][str(op.message.to)] = False
                        line.sendMessage(op.message.to,"LeaveGroupMessage turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!unsentgroupmsg on":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Unsend_Msg"][str(op.message.to)] == True:
                        line.sendMessage(op.message.to,"UnsentGroupMessage already ON.")
                    else:
                        Settings["Unsend_Msg"][str(op.message.to)] = True
                        line.sendMessage(op.message.to,"UnsentGroupMessage turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            elif op.message.text.lower() == "!unsentgroupmsg off":
                if op.message._from in Privilege['Staff'][str(op.message.to)] or op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Settings["Unsend_Msg"][str(op.message.to)] == False:
                        line.sendMessage(op.message.to,"UnsentGroupMessage already OFF.")
                    else:
                        Settings["Unsend_Msg"][str(op.message.to)] = False
                        line.sendMessage(op.message.to,"UnsentGroupMessage turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Staff or higher permission required.")
            # Staff inside group only op.message.text Command list # End
            #---#
            # Admin inside group only op.message.text Command list # Start
            elif "!admin add @" in op.message.text.lower():
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if targets in Privilege['Creator']:
                        line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                    elif targets in Privilege['Admin'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"Already an admin.")
                    elif targets in Privilege['Staff'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"New rank!\nFrom Staff->Admin >_<\"")
                        Privilege['Staff'][str(op.message.to)].remove(targets)
                        Privilege['Admin'][str(op.message.to)].append(targets)
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        Privilege['Admin'][str(op.message.to)].append(targets)
                        line.sendMessage(op.message.to,"Promoted as an Admin.")
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            elif "!admin add " in op.message.text.lower():
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[11:]
                        if targets in Privilege['Creator']:
                            line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                        elif targets in Privilege['Admin'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"Already an admin.")
                        elif targets in Privilege['Staff'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"New rank!\nFrom Staff->Admin >_<\"")
                            Privilege['Staff'][str(op.message.to)].remove(targets)
                            Privilege['Admin'][str(op.message.to)].append(targets)
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                        else:
                            Privilege['Admin'][str(op.message.to)].append(targets)
                            line.sendMessage(op.message.to,"Promoted as an Admin.")
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            elif op.message.text.lower() == "!cleangroup":
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    gs = line.getGroup(op.message.to)
                    line.sendMessage(op.message.to,"Group cleaning begin.")
                    line.sendMessage(op.message.to,"Goodbye >_<")
                    targets = []
                    for g in gs.members:
                        targets.append(g.mid)
                    # --------------[admin and staff MID]----------------
                    for Adm in Privilege['Admin'][str(op.message.to)]:
                        targets.remove(Adm)
                    for Stf in Privilege['Staff'][str(op.message.to)]:
                        targets.remove(Stf)
                    for Crt in Privilege['Creator']:
                        targets.remove(Crt)
                    # --------------[Bot and admin MID]----------------
                    if targets == []:
                        line.sendMessage(op.message.to,"No Members.")
                    else:
                        for target in targets:
                            try:
                                line.kickoutFromGroup(op.message.to,[target])
                            except Exception as e:
                                print(e)
                                line.sendMessage(op.message.to,"Group cleaned.")
                                return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            elif op.message.text.lower() == "!kickban":
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    if Privilege['BlackList'][str(op.message.to)] == []:
                        line.sendMessage(op.message.to,"It looks empty here.")
                    else:
                        line.sendMessage(op.message.to,"Removing blacklisted users.")
                        for jj in Privilege['BlackList'][str(op.message.to)]:
                            line.kickoutFromGroup(op.message.to,[jj])
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            elif "!staff remove @" in op.message.text.lower():
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if targets in Privilege['Creator']:
                        line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                    elif targets in Privilege['Admin'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"It's admin, Not staff.")
                    elif targets in Privilege['Staff'][str(op.message.to)]:
                        Privilege['Staff'][str(op.message.to)].remove(targets)
                        line.sendMessage(op.message.to,"Removed from the staff list.")
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    else:
                        line.sendMessage(op.message.to,"Dia hanya warganet biasa.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            elif "!staff remove " in op.message.text.lower():
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[14:]
                        if targets in Privilege['Creator']:
                            line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                        elif targets in Privilege['Admin'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"It's admin, Not staff.")
                        elif targets in Privilege['Staff'][str(op.message.to)]:
                            Privilege['Staff'][str(op.message.to)].remove(targets)
                            line.sendMessage(op.message.to,"Removed from the staff list.")
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                        else:
                            line.sendMessage(op.message.to,"Dia hanya warganet biasa.")
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            elif op.message.text.lower() == "!bye":
                if op.message._from in Privilege['Admin'][str(op.message.to)] or op.message._from in Privilege['Creator']:
                    try:
                        line.sendMessage(op.message.to,"Good Bye~\nThanks~ >_<\"")
                        line.leaveGroup(op.message.to)
                    except Exception as e:
                        print(e)
                        pass
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Admin permission required.")
            # Admin inside group only op.message.text Command list # End
            #---#
            # Requested feature Command list # Start
            elif "!broadcast " in op.message.text.lower():
                if op.message._from in Privilege['Creator'] or op.message._from in broadcaster:
                    if op.message._from in broadcaster:
                        broadcaster.remove(str(op.message._from))
                    bctxt = op.message.text[11:]
                    n = line.getGroupIdsJoined()
                    for daftarGroup in n:
                        line.sendMessage(daftarGroup, (bctxt))
                    line.sendMessage(op.message.to,"BroadCast sent.")
                else:
                    line.sendMessage(op.message.to,"You have no access this feature.")
                    line.sendMessage(op.message.to,"Please request access by chat via private message.")
            # Requested feature Command list # Start
            #---#
            # Creator only Command list # Start
            elif "!add @" in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found or already added.")
                        return
                    try:
                        line.findAndAddContactsByMid(targets)
                        line.sendMessage(op.message.to,"Added.")
                    except Exception as e:
                        line.log("[RECEIVE_MESSAGE] ERROR : " + str(e))
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!add " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[5:]
                        line.findAndAddContactsByMid(targets)
                        line.sendMessage(op.message.to,"Added.")
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found or already added.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!autojoin on":
                if op.message._from in Privilege['Creator']:
                    if Settings["Auto_JoinGroup"] == True:
                        line.sendMessage(op.message.to,"Auto join already ON.")
                    else:
                        Settings["Auto_JoinGroup"] = True
                        line.sendMessage(op.message.to,"Auto join turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!autojoin off":
                if op.message._from in Privilege['Creator']:
                    if Settings["Auto_JoinGroup"] == False:
                        line.sendMessage(op.message.to,"Auto join already OFF.")
                    else:
                        Settings["Auto_JoinGroup"] = False
                        line.sendMessage(op.message.to,"Auto join turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!allowbroadcast @" in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    broadcaster.append(str(targets))
                    line.sendMessage(op.message.to,"You have only 1x broadcast feature.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!allowbroadcast " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[16:]
                        broadcaster.append(str(targets))
                        line.sendMessage(op.message.to,"You have only 1x broadcast feature.")
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!admin remove @" in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    targets = ""
                    try:
                        key = eval(op.message.contentMetadata["MENTION"])
                        mmid = key["MENTIONEES"][0]["M"]
                        targets = mmid
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                    if targets in Privilege['Creator']:
                        line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                    elif targets in Privilege['Admin'][str(op.message.to)]:
                        Privilege['Admin'][str(op.message.to)].remove(targets)
                        line.sendMessage(op.message.to,"Removed from the admin list.")
                        with open('Privilege.bin', 'wb') as pickle_out:
                            pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                    elif targets in Privilege['Staff'][str(op.message.to)]:
                        line.sendMessage(op.message.to,"It's staff. Not admin.")
                    else:
                        line.sendMessage(op.message.to,"Dia hanya warganet biasa.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!admin remove " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    try:
                        targets = op.message.text[14:]
                        if targets in Privilege['Creator']:
                            line.sendMessage(op.message.to,"It's Creator,\nCan't touch this.")
                        elif targets in Privilege['Admin'][str(op.message.to)]:
                            Privilege['Admin'][str(op.message.to)].remove(targets)
                            line.sendMessage(op.message.to,"Removed from the admin list.")
                            with open('Privilege.bin', 'wb') as pickle_out:
                                pickle.dump(Privilege, pickle_out, pickle.HIGHEST_PROTOCOL)
                        elif targets in Privilege['Staff'][str(op.message.to)]:
                            line.sendMessage(op.message.to,"It's staff. Not admin.")
                        else:
                            line.sendMessage(op.message.to,"Dia hanya warganet biasa.")
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to,"Contact not found.")
                        return
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!pesan " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    try:
                        line.sendMessage(op.message.text[7:40], op.message.text[41:])
                        line.sendMessage(op.message.to, "Message sent to " + line.getContact(op.message.text[7:40]).displayName)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to, "Contact not found.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!changename " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    BotVersionNew = line.getProfile()
                    BotVersionNew.displayName = op.message.text[12:32].rstrip()
                    line.updateProfile(BotVersionNew)
                    line.sendMessage(op.message.to, "displayName changed.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!changestatus " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    BotStatusNew = line.getProfile()
                    BotStatusNew.statusMessage = op.message.text[14:514].strip()
                    line.updateProfile(BotStatusNew)
                    line.sendMessage(op.message.to, "profileStatus changed.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!viewcontacts":
                if op.message._from in Privilege['Creator']:
                    AllContacts = line.getAllContactIds()
                    ListContacts = "List Contacts\n"
                    for Ctcts in AllContacts:
                        ListContacts += "\n" + line.getContact(Ctcts).displayName + "\n" + Ctcts + "\n"
                    line.sendMessage(op.message.to, ListContacts.rstrip())
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!viewinvitedgroups":
                if op.message._from in Privilege['Creator']:
                    AllInvGroups = line.getGroupIdsInvited()
                    ListInvGroups = "List Invited Group\n"
                    for GrpInvs in AllInvGroups:
                        ListInvGroups += "\n" + line.getGroup(GrpInvs).name + "\n" + GrpInvs + "\n"
                    line.sendMessage(op.message.to, ListInvGroups.rstrip())
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!viewjoinedgroups":
                if op.message._from in Privilege['Creator']:
                    AllJndGroups = line.getGroupIdsJoined()
                    ListJndGroups = "List Joined Group\n"
                    for GrpJnds in AllJndGroups:
                        ListJndGroups += "\n" + line.getGroup(GrpJnds).name + "\n" + GrpJnds + "\n"
                    line.sendMessage(op.message.to, ListJndGroups.rstrip())
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!joingroup " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    grpIDinv = op.message.text[11:]
                    try:
                        line.sendMessage(op.message.to, "Joining group " + line.getGroup(grpIDinv).name)
                        line.acceptGroupInvitation(grpIDinv)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to, "This Group doesn't exists or already joined.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!leavegroup " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    grpIDleave = op.message.text[12:]
                    try:
                        line.sendMessage(op.message.to, "Leaving group " + line.getGroup(grpIDleave).name)
                        line.leaveGroup(grpIDleave)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to, "This Group doesn't exists or already left.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif "!rejectgroup " in op.message.text.lower():
                if op.message._from in Privilege['Creator']:
                    grpIDreject = op.message.text[13:]
                    try:
                        line.sendMessage(op.message.to, "Rejecting group " + line.getGroup(grpIDreject).name)
                        line.rejectGroupInvitation(grpIDreject)
                    except Exception as e:
                        print(e)
                        line.sendMessage(op.message.to, "You aren't invited or already rejected.")
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!autoadd on":
                if op.message._from in Privilege['Creator']:
                    if Settings["Auto_Add"] == True:
                        line.sendMessage(op.message.to,"Auto Add already ON.")
                    else:
                        Settings["Auto_Add"] = True
                        line.sendMessage(op.message.to,"Auto Add turned ON.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            elif op.message.text.lower() == "!autoadd off":
                if op.message._from in Privilege['Creator']:
                    if Settings["Auto_Add"] == False:
                        line.sendMessage(op.message.to,"Auto Add already OFF.")
                    else:
                        Settings["Auto_Add"] = False
                        line.sendMessage(op.message.to,"Auto Add turned OFF.")
                        with open('Settings.bin', 'wb') as pickle_out:
                            pickle.dump(Settings, pickle_out, pickle.HIGHEST_PROTOCOL)
                else:
                    line.sendMessage(op.message.to,"Command denied.")
                    line.sendMessage(op.message.to,"Creator permission required.")
            # Creator only op.message.text Command list # End
            else:
                return
    return

# Save Ke Chat Log
# op.message.toType = 0 => Private Chat
# op.message.toType = 2 => Group Chat
# op.message.contentType = 0 => Text
# op.message.contentType = 1 => Photo
# op.message.contentType = 2 => Video
# op.message.contentType = 3 => Voice Chat
# op.message.contentType = 6 => Video / Voice Call
# op.message.contentType = 7 => Sticker
# op.message.contentType = 13 => Line Contact
# op.message.contentType = 14 => Files
# op.message.contentType = 16 => Create Notes / Albums
# op.message.contentType = 18 => Delete Notes / Albums
# op.message._from = UserID pengirim pesan di group
# op.message.to = GroupID
def SAVE_CHAT(op):
    try:
        ChatLog[op.message.id] = {
            "text": op.message.text,
            "from": op.message._from,
            "group": op.message.to,
            "createdTime": op.message.createdTime,
            "contentType": op.message.contentType,
            "contentMetadata": op.message.contentMetadata
        }
    except Exception as e1:
        print(e)
        try:
            ChatLog[op.message.id] = {
                "text": op.message.text,
                "from": op.message._from,
                "createdTime": op.message.createdTime,
                "contentType": op.message.contentType,
                "contentMetadata": op.message.contentMetadata
            }
        except Exception as e:
            print(e)

# Kita ngirim pesan # op.type=25
def SEND_MESSAGE(op):
    SAVE_CHAT(op)
    try: # Group Message
        ginfo = line.getGroup(op.message.to) # Get group info
        BOT_COMMANDS(op, ginfo)
    except Exception as e: # Private Message
        print(e)
        # line.log('[SEND_MESSAGE] [%s -> %s] %s' % (line.getContact(mid).displayName, line.getContact(op.message.to).displayName, op.message.text))
    return
    
# Kita menerima pesan # op.type=26
def RECEIVE_MESSAGE(op):
    SAVE_CHAT(op)
    if op.message.toType == 2: # Group Message
        ginfo = line.getGroup(op.message.to) # Get group info
        BOT_COMMANDS(op, ginfo)
    elif op.message.toType == 0: # Private Message
        contact = line.getContact(op.message._from) # Get sender contact
        # line.log('[RECEIVE_MESSAGE] [%s -> %s] %s' % (contact.displayName, line.getContact(mid).displayName, op.message.text))
        if op.message._from in Privilege['Creator']:
            # Creator Editing Bot Profile, Status, Foto, TimeLine, PrivateMessage, etc.
            if "!pesan " in op.message.text.lower():
                try:
                    line.sendMessage(op.message.text[7:40], op.message.text[41:])
                    line.sendMessage(op.message.to, "Message sent to " + line.getContact(op.message.text[7:40]).displayName)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message._from, "Contact not found.")
            elif "!changename " in op.message.text.lower():
                BotVersionNew = line.getProfile()
                BotVersionNew.displayName = op.message.text[12:32].rstrip()
                line.updateProfile(BotVersionNew)
                line.sendMessage(op.message.to, "displayName changed.")
            elif "!changestatus " in op.message.text.lower():
                BotStatusNew = line.getProfile()
                BotStatusNew.statusMessage = op.message.text[14:514].strip()
                line.updateProfile(BotStatusNew)
                line.sendMessage(op.message._from, "profileStatus changed.")
            elif op.message.text.lower() == "!viewcontacts":
                AllContacts = line.getAllContactIds()
                ListContacts = "List Contacts\n"
                for Ctcts in AllContacts:
                    ListContacts += "\n" + line.getContact(Ctcts).displayName + "\n" + Ctcts + "\n"
                line.sendMessage(op.message._from, ListContacts.rstrip())
            elif op.message.text.lower() == "!viewinvitedgroups":
                AllInvGroups = line.getGroupIdsInvited()
                ListInvGroups = "List Invited Group\n"
                for GrpInvs in AllInvGroups:
                    ListInvGroups += "\n" + line.getGroup(GrpInvs).name + "\n" + GrpInvs + "\n"
                line.sendMessage(op.message._from, ListInvGroups.rstrip())
            elif op.message.text.lower() == "!viewjoinedgroups":
                AllJndGroups = line.getGroupIdsJoined()
                ListJndGroups = "List Joined Group\n"
                for GrpJnds in AllJndGroups:
                    ListJndGroups += "\n" + line.getGroup(GrpJnds).name + "\n" + GrpJnds + "\n"
                line.sendMessage(op.message._from, ListJndGroups.rstrip())
            elif "!joingroup " in op.message.text.lower():
                grpIDinv = op.message.text[11:]
                try:
                    line.sendMessage(op.message._from, "Joining group " + line.getGroup(grpIDinv).name)
                    line.acceptGroupInvitation(grpIDinv)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message._from, "This Group doesn't exists or already joined.")
            elif "!leavegroup " in op.message.text.lower():
                grpIDleave = op.message.text[12:]
                try:
                    line.sendMessage(op.message._from, "Leaving group " + line.getGroup(grpIDleave).name)
                    line.leaveGroup(grpIDleave)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message._from, "This Group doesn't exists or already left.")
            elif "!rejectgroup " in op.message.text.lower():
                grpIDreject = op.message.text[13:]
                try:
                    line.sendMessage(op.message._from, "Rejecting group " + line.getGroup(grpIDreject).name)
                    line.rejectGroupInvitation(grpIDreject)
                except Exception as e:
                    print(e)
                    line.sendMessage(op.message._from, "You aren't invited or already rejected.")
            else:
                for MsgToCrt in Privilege['Creator']:
                    if MsgToCrt == mid or MsgToCrt == op.message._from:
                        pass
                    else:
                        line.sendMessage(MsgToCrt, "From: " + contact.displayName + "\n\nmID: " + op.message._from + "\n\nMessages: \n" + op.message.text)
        else:
            KirimCreatorLain = True
            # Dipanggil Namanya
            if op.message.text.lower() in ['bi', 'yas', 'ias', 'basilius', 'bias', 'astho', 'christyono', 'bas']:
                if "u8a43bfe119402c69fe12fb5cdb95b7b3" in mid:
                    PanggilPM = ['Ya, Ada apa?', 'Ya, Ada yang bisa dibantu?', 'Ya, Kenapa?', 'He?']
                    KirimCreatorLain = False
                    line.sendMessage(op.message._from, random.choice(PanggilPM))
            # Dikatain BOT
            if "ngebot" in op.message.text.lower() or " bot" in op.message.text.lower() or "bot " in op.message.text.lower():
                DikatainBOT = ['Aku Bukan BOT!\nIh bikin kesel~', 'BOT? Ha?\nAku hanya perantara~', 'So? What?\nHanya pengganti saat Bias sedang pergi~']
                KirimCreatorLain = False
                line.sendMessage(op.message._from, random.choice(DikatainBOT))
            # Kirim Ke Creator Lain
            if KirimCreatorLain == True:
                for MsgToCrt in Privilege['Creator']:
                    if MsgToCrt == mid:
                        pass
                    else:
                        line.sendMessage(MsgToCrt, "From: " + contact.displayName + "\n\nmID: " + op.message._from + "\n\nMessages: \n" + op.message.text)
    return

# Mengetahui Siapa saja yang sudah read pesan kita # op.type=28
# op.param1 = UserID yang nge-read op.message.text kita
# op.param2 = MessagesID (bisa banyak)
def RECEIVE_MESSAGE_RECEIPT(op):
    return

# Kita membatalkan invite pending group # op.type=31
# op.param1 = GroupID
# op.param2 = UserID yang kita cancel
def CANCEL_INVITATION_GROUP(op):
    return

# Orang lain meng-cancel invitan di group # op.type=32
# op.param1 = GroupID
# op.param2 = UserID yang meng-cancel
# op.param3 = UserID yang di-cancel
def NOTIFIED_CANCEL_INVITATION_GROUP(op):
    return

# Kita menolak Invite group # op.type=34
# op.param1 = GroupID yang kita tolak
def REJECT_GROUP_INVITATION(op):
    return

# Orang lain membatalkan Invit-an group (kita dalam group) # op.type=35
# Gak penting banget yak harus tau .. wkwkwk
def NOTIFIED_REJECT_GROUP_INVITATION(op):
    return

# Kita update settings # op.type=36
# op.param1 = Attribut yang di ganti
# op.param1 = Misteri ga jelas ni kayaknya boolean
# Refresh terus pake getSettingsAttributes() atau getSettings()
def UPDATE_SETTINGS(op):
    return

# Chat ditandain telah dibaca # op.type=40
def SEND_CHAT_CHECKED(op):
    return

# Menghapus history chat # op.type=41
# op.param1 = UserID / GroupID / RoomID
# op.param2 = Angka ga jelas ini Au'paan
def SEND_CHAT_REMOVED(op):
    return

# Update kontak settings hidden / display # op.type=49
# op.param1 = UserID yang di update status hidden / shown-nya
# op.param2 = Attribut yang di ganti
def UPDATE_CONTACT(op):
    return

# Read mark in group # op=55
# op.param1 = GroupID
# op.param2 = Yang nge-Read
def NOTIFIED_READ_MESSAGE(op):
    try: # Group Message
        ginfo = line.getGroup(op.param1)
        line.log("[NOTIFIED_READ_MESSAGE] [%s] [%s]" % (ginfo.name, line.getContact(op.param2).displayName))
        if op.param1 in SilentReader['readPoint']:
            Name = line.getContact(op.param2).displayName
            if Name in SilentReader['readMember'][str(op.param1)]:
                pass
            else:
                SilentReader['readMember'][str(op.param1)] += "\n- " + Name
                SilentReader['ROM'][str(op.param1)][str(op.param2)] = "- " + Name
        else:
            pass
    except Exception as e: # Private Message
        print(e)
        try:
            line.log("[NOTIFIED_READ_MESSAGE] [%s]" % (line.getContact(op.param2).displayName))
        except Exception as e:
            line.log("[NOTIFIED_READ_MESSAGE] ERROR : " + str(e))
    return

# Ga tau apa # op.type=60
# Muncul setelah NOTIFIED_ACCEPT_GROUP_INVITATION dan NOTIFIED_INVITE_INTO_ROOM
# op.param1 = GroupID
# op.param2 = GroupID juga tapi lain
def MYSTERY1(op):
    return

# Ga tau apa juga ini terakhir # op.type=61
# Muncul setelah NOTIFIED_LEAVE_GROUP, KICKOUT_FROM_GROUP, NOTIFIED_KICKOUT_FROM_GROUP, dan NOTIFIED_LEAVE_ROOM
# op.param1 = GroupID
# op.param2 = GroupID lain
# op.param3 = 0
def MYSTERY2(op):
    return

# Destroy Message # op.type=65
# op.param1 = Waktu pengiriman sebelum unsend
# op.param2 = ID pesan yang di unsend
def NOTIFIED_DESTROY_MESSAGE(op):
    try:
        if Settings["Unsend_Msg"][str(ChatLog[op.param2]['group'])] == True:
            if ChatLog[op.param2]['contentType'] == 0:
                line.sendMessageWithMention(ChatLog[op.param2]['group'],"[DESTROY_MSG] [list] %s" % (ChatLog[op.param2]['text']), [ChatLog[op.param2]['from']])
    except Exception as e:
        line.log("[NOTIFIED_DESTROY_MESSAGE] ERROR : " + str(e))
    return

# Fungsi yang dipake saja
oepoll.addOpInterruptWithDict({
    OpType.END_OF_OPERATION: END_OF_OPERATION, #0
    OpType.UPDATE_PROFILE: UPDATE_PROFILE, #1
    OpType.NOTIFIED_UPDATE_PROFILE: NOTIFIED_UPDATE_PROFILE, #2
    OpType.REGISTER_USERID: REGISTER_USERID, #3
    OpType.ADD_CONTACT: ADD_CONTACT, #4
    OpType.NOTIFIED_ADD_CONTACT: NOTIFIED_ADD_CONTACT, #5
    OpType.BLOCK_CONTACT: BLOCK_CONTACT, #6
    OpType.UNBLOCK_CONTACT: UNBLOCK_CONTACT, #7
    OpType.CREATE_GROUP: CREATE_GROUP, #9
    OpType.UPDATE_GROUP: UPDATE_GROUP, #10
    OpType.NOTIFIED_UPDATE_GROUP: NOTIFIED_UPDATE_GROUP, #11
    OpType.INVITE_INTO_GROUP: INVITE_INTO_GROUP, #12
    OpType.NOTIFIED_INVITE_INTO_GROUP: NOTIFIED_INVITE_INTO_GROUP, #13
    OpType.LEAVE_GROUP: LEAVE_GROUP, #14
    OpType.NOTIFIED_LEAVE_GROUP: NOTIFIED_LEAVE_GROUP, #15
    OpType.ACCEPT_GROUP_INVITATION: ACCEPT_GROUP_INVITATION, #16
    OpType.NOTIFIED_ACCEPT_GROUP_INVITATION: NOTIFIED_ACCEPT_GROUP_INVITATION, #17
    OpType.KICKOUT_FROM_GROUP: KICKOUT_FROM_GROUP, #18
    OpType.NOTIFIED_KICKOUT_FROM_GROUP: NOTIFIED_KICKOUT_FROM_GROUP, #19
    OpType.CREATE_ROOM: CREATE_ROOM, #20
    OpType.INVITE_INTO_ROOM: INVITE_INTO_ROOM, #21
    OpType.NOTIFIED_INVITE_INTO_ROOM: NOTIFIED_INVITE_INTO_ROOM, #22
    OpType.LEAVE_ROOM: LEAVE_ROOM, #23
    OpType.NOTIFIED_LEAVE_ROOM: NOTIFIED_LEAVE_ROOM, #24
    OpType.SEND_MESSAGE: SEND_MESSAGE, #25
    OpType.RECEIVE_MESSAGE: RECEIVE_MESSAGE, #26
    OpType.RECEIVE_MESSAGE_RECEIPT: RECEIVE_MESSAGE_RECEIPT, #28
    OpType.CANCEL_INVITATION_GROUP: CANCEL_INVITATION_GROUP, #31
    OpType.NOTIFIED_CANCEL_INVITATION_GROUP: NOTIFIED_CANCEL_INVITATION_GROUP, #32
    OpType.REJECT_GROUP_INVITATION: REJECT_GROUP_INVITATION, #34
    OpType.NOTIFIED_REJECT_GROUP_INVITATION: NOTIFIED_REJECT_GROUP_INVITATION, #35
    OpType.UPDATE_SETTINGS: UPDATE_SETTINGS, #36
    OpType.SEND_CHAT_CHECKED: SEND_CHAT_CHECKED, #40
    OpType.SEND_CHAT_REMOVED: SEND_CHAT_REMOVED, #41
    OpType.UPDATE_CONTACT: UPDATE_CONTACT, #49
    OpType.NOTIFIED_READ_MESSAGE: NOTIFIED_READ_MESSAGE, #55
    OpType.NOTIFIED_DESTROY_MESSAGE: NOTIFIED_DESTROY_MESSAGE #65
})

JumlahLoop = 0

while True:
    # Nunggu chat terus nentuin op
    oepoll.trace()
    JumlahLoop += 1
    if JumlahLoop >= 10:
        JumlahLoop = 0
        with open('SilentReader.bin', 'wb') as pickle_out:
            pickle.dump(SilentReader, pickle_out, pickle.HIGHEST_PROTOCOL)