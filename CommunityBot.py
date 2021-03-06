import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import datetime
import pickle
import os
from steem import Steem
from steem.converter import Converter
from steem.post import Post
import csv
import sqlite3
import math
import locale
from pytz import timezone


locale.setlocale(locale.LC_ALL,'')


db = sqlite3.connect("articles.db", detect_types=sqlite3.PARSE_DECLTYPES) # initializing the db that will hold the articles to be voted

c  = db.cursor()
# initial creation of the table for the articles, uncomment if necessary
#c.execute(''' CREATE TABLE articles
#              (kurator text, permlink text, votes real)''') 
#c.execute(''' CREATE TABLE meetup
#              (planer text, ort text, permlink text, datum timestamp)''') 
db.commit()

Client = discord.Client()
client = commands.Bot(command_prefix = "?") # currently not used
fname = "save.txt" # Define the filename for the registered users data


if os.path.isfile(fname): # routine to either open an existing file or create a new empty one
    liste = pickle.load(open(fname,"rb")) 
else: 
    print ("File %s does not exist, creating a new one!" % fname)
    liste={}


s=Steem()
    
@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")

@client.event
async def printhelp(message): #function to print out help and usage methods
        embed = discord.Embed(title="D-A-CH Support Help", description="Befehle und Hilfe", color=0x00ff00)
        #embed.add_field(name="§register", value="Benutzung: §register gefolgt vom Steemnamen eingeben um die Verbindung DiscordID und SteemID zu schaffen", inline=False)
        embed.add_field(name="?status", value="Benutzung: ?status gibt die registrierten Benutzer und den Status des SteemBots zurück", inline=False)
        embed.add_field(name="?help oder ?hilfe", value="Benutzung: ?help gibt diese Hilfe zurück", inline=False)
        embed.add_field(name="?nextmeetup", value="Benutzung: ?nextmeetup gibt die nächsten Meetups mit allen Infos aus", inline=False)
        embed.add_field(name="?info", value="Benutzung: ?info + steemname gibt Infos zum Steem Account aus, Beispiel ?info dach-support", inline=False)
        
        embed.set_thumbnail(url="https://steemitimages.com/DQmSxg3TwiR7ZcTdH9WKH2To48eJsdQ7D1ejpYUmvLtuzUk/steemitdachfullress.png")
        await client.send_message(message.channel, embed=embed)

@client.event
async def on_message(message):
    command_run=0
    #if message.content.upper().startswith("§REGISTER"): # code for the !register command
#        userID = message.author.id
#        if (len(message.content.strip()) > 9):
#            args = message.content.split(" ")
#            if "@" in args[1]:
#                await client.send_message(message.channel, "Fehler -- Bitte Steem ID ohne @ eingeben!")
#            else:    
#                command_run = 1
#                if userID not in liste and args[1] not in liste :    
#                    liste[userID] = args[1] # append the userid and the steem handle to the dict
#                    await client.send_message(message.channel, "Für die Discord ID <@%s> wurde die Steem ID %s registriert !" % (userID,liste[userID]) )
#                    f = open(fname,"wb") #write the dict into a file
#                    pickle.dump(liste,f)
#                    f.close()
#
#                else:
#                    await client.send_message(message.channel, "Die Discord ID <@%s> ist bereits mit der Steem ID %s verknüpft!" % (userID,liste[userID]) )
#                    print (liste)           
                          
                    
    if message.content.upper().startswith("?STATUS"): # code for the status command, will list users and basic data about the bot
        account_name="dach-support"
        acc_data = s.get_account(account_name)
        votingpower=float(acc_data["voting_power"])
        votingpower = votingpower / 100
        votetime = acc_data["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
        votetime = votetime.replace("T", " ")
        votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        time_vp = now - votetime
        percentup = (int(((time_vp.total_seconds())/60)-60)*0.0139)
        if ((votingpower+percentup)>100): # capping the vote percentage at 100 
            resulting_vp = 100
        else:
            resulting_vp = (votingpower+percentup)
        embed = discord.Embed(title="D-A-CH Support Status", description="Alive and kickin!", color=0x00ff00)
        embed.add_field(name="Angemeldete User", value=liste, inline=False)
        embed.add_field(name="Votingpower", value="%.2f Prozent" % resulting_vp, inline=False)
        embed.set_thumbnail(url="https://steemitimages.com/DQmSxg3TwiR7ZcTdH9WKH2To48eJsdQ7D1ejpYUmvLtuzUk/steemitdachfullress.png")
        await client.send_message(message.channel, embed=embed)
        command_run = 1
        
        
    if message.content.upper().startswith("?HELP") or message.content.upper().startswith("§HILFE") : # code for the help function
        await printhelp(message)
        command_run = 1

        
    if message.content.upper().startswith("?INFO"): # code for the status command, will list users and basic data about the bot
        args = message.content.split(" ")
        try:
            account_name = str(args[1])
            try:
                today = datetime.datetime.today()
                sbd = s.get_account(account_name)
                pos1 = (str(sbd["json_metadata"]))
                posanf = pos1.find("profile_image")
                if posanf == -1:
                    picurl="https://coinjournal.net/wp-content/uploads/2016/06/steemit-logo-blockchain-social-media-platform-696x364.png"
                else:
                    posanf = posanf +16
                    posend = pos1.find("\"",posanf)
                    picurl = (pos1[posanf:posend]) 
                    
                steemlink = "https://steemit.com/@"+ account_name
                cachedlink=("https://steemitimages.com/u/%s/avatar" % account_name)
                #print (sbd)
                #print (cachedlink)
                #profilepic = "https://img.busy.org/@" + account_name
                votingpower=float(sbd["voting_power"])
                votingpower = votingpower / 100
                SPown = sbd["vesting_shares"].replace("VESTS","") ## start of calculation of most recent Steempower value
                SPout = sbd["delegated_vesting_shares"].replace("VESTS","")
                SPout = float(SPout)
                SPown = float(SPown)
                SPin = sbd["received_vesting_shares"].replace("VESTS","")
                SPin = float(SPin)
                conv=Converter()
                steempower = conv.vests_to_sp(SPown)
                steempower_out = conv.vests_to_sp(SPout)
                steempower_in = conv.vests_to_sp(SPin)
                resulting_steempower = steempower - steempower_out + steempower_in
                #locales formating
                steempower = locale.format("%.2f",float(steempower), grouping = True)
                steempower_out = locale.format("%.2f",float(steempower_out), grouping = True)
                steempower_in = locale.format("%.2f",float(steempower_in), grouping = True)
                resulting_steempower = locale.format("%.2f",float(resulting_steempower), grouping = True)
                
                votetime = sbd["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
                votetime = votetime.replace("T", " ")
                votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
                created = sbd["created"]
                created = created.replace("T", " ")
                created = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
                since = today - created
                rep = sbd["reputation"] # startpoint of the rep calculation out of the raw reputation
                rep = float(rep)
                if rep == 0: # special situation for the new accounts or the ones that never have received a single vote
                    rep = 25
                else:
                    neg = rep < 0
                    rep = abs(rep)
                    rep = math.log10(rep)
                    rep = max(rep - 9, 0)
                    rep = (-1 if neg else 1) * rep
                    rep = rep * 9 + 25
                    rep = round(rep, 2)
                    rep = locale.format("%.2f",rep, grouping = False) #locale format
                    
                now = datetime.datetime.now() # start of the calculation of the current voting power
                time_vp = now - votetime
                percentup = (int(((time_vp.total_seconds())/60)-60)*0.0139)
                if ((votingpower+percentup)>100): # capping the vote percentage at 100 
                    resulting_vp = 100
                else:
                    resulting_vp = (votingpower+percentup)
                resulting_vp = locale.format("%.2f",resulting_vp)
                
                time_comment = sbd["last_post"] # start of caluclation of last activity information
                time_comment = time_comment.replace("T", " ")
                time_comment = datetime.datetime.strptime(time_comment, "%Y-%m-%d %H:%M:%S")
                time_post = sbd["last_root_post"] 
                time_post = time_post.replace("T", " ")
                time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
                latestactivity = max((votetime,time_comment,time_post))
                latestactivity = latestactivity.replace(tzinfo=timezone('UTC'))
                latestactivity_cet = latestactivity.astimezone(timezone('Europe/Berlin')) 
                #building and localizing the amount of steem and savings
                amount_steem = (sbd["balance"].replace(" STEEM",""))
                amount_steem =  locale.format("%.2f",float(amount_steem), grouping = True)
                amount_steem_savings = (sbd["savings_balance"].replace(" STEEM",""))
                amount_steem_savings = locale.format("%.2f",float(amount_steem_savings), grouping = True)
                #building and localizing the amount of sbd and savings
                amount_sbd = (sbd["sbd_balance"].replace(" SBD",""))
                amount_sbd =  locale.format("%.2f",float(amount_sbd), grouping = True)
                amount_sbd_savings = (sbd["savings_sbd_balance"].replace(" SBD",""))
                amount_sbd_savings = locale.format("%.2f",float(amount_sbd_savings),grouping = True)
                
                
                
                # building the embed to broadcast via discor
                embed = discord.Embed(title="Account Information", description="[%s](%s)"% (account_name,steemlink), color=0x00ff00)
                embed.add_field(name="Steem Power", value="%s SP" % resulting_steempower)
                embed.add_field(name="Eigene SP", value="%s SP" % steempower)
                embed.add_field(name="Delegierte SP", value="%s SP" % steempower_out )
                embed.add_field(name="Erhaltene SP", value="%s SP" % steempower_in )
                embed.add_field(name="Votingpower", value="%s Prozent" % resulting_vp)
                embed.add_field(name="Kontostand Steem (Save)", value="%s (%s) STEEM" % (amount_steem,amount_steem_savings))
                embed.add_field(name="Kontostand SBD (Save)", value="%s (%s) SBD"% (amount_sbd,amount_sbd_savings))
                embed.add_field(name="Angemeldet seit", value="%s, %s Tage" % (datetime.datetime.strftime(created,"%d.%m.%Y"),since.days))
                embed.add_field(name="Reputation", value=rep)
                embed.add_field(name="Letzte Aktion auf Steem", value=datetime.datetime.strftime(latestactivity_cet,"%d.%m.%Y %H:%M"))
                
                embed.set_thumbnail(url=picurl)
                embed.timestamp=datetime.datetime.utcnow()
                embed.set_footer(text="frisch von der Blockchain")
                await client.send_message(message.channel, embed=embed) # send the built message
                command_run = 1
            except TypeError as err:
                await client.send_message(message.channel, "Fehler - kein SteemAccount mit dem Namen %s gefunden" % account_name)
                print (err)
                command_run = 1
        except IndexError as err:
            await client.send_message(message.channel, "Fehler - bitte Steemnamen nach §info eingeben")
            print (err)
            command_run = 1
        
    
#    if message.content.upper().startswith("§UPVOTE"): # code for the upvote command, writes the article and the author into a file to be used by the vote bot
#        if (len(message.content.strip()) > 7) and message.content[7] == " ":
#            args = message.content.split(" ")
#            pos1 = args[1].find("@")
#            check = 0
#            if pos1 <= 0:
#                await client.send_message(message.channel, "Fehler - Bitte den kompletten Link hinter §upvote einfügen, beginnend mit http...")
#                check = check +1
#            else:
#                pos2 = args[1].find("/",pos1)
#                steem_name = (args[1][pos1+1:pos2])
#                length = len(args[1])
#                article = Post(args[1][pos1:length])
#                elapsed = Post.time_elapsed(article)
#                if elapsed >= datetime.timedelta(days=3):
#                    await client.send_message(message.channel, "Fehler - Leider ist der Post älter als 3 Tage")
#                    check = check +1
#                    command_run = 1
#                if article.is_main_post() is False:
#                    await client.send_message(message.channel, "Fehler - Kommentare können nicht vorgeschlagen werden")
#                    check = check +1
#                    command_run = 1
#                #await client.send_message(message.channel, "Alter des Posts : %s " % elapsed) 
#        
#                userID = message.author.id
#                if userID in liste:
#                    registered_name = liste[userID]
#                    if steem_name == registered_name:
#                        await client.send_message(message.channel, "Fehler - Das Vorschlagen eigener Posts ist untersagt!")
#                        check = check +1
#                else:
#                    await client.send_message(message.channel, "Fehler - Dein Steemname ist nicht registriert -- bitte zuerst §register benutzen")
#                    check = check +1
#                c.execute("SELECT permlink FROM articles WHERE permlink = (?)", (args[1][pos1:length],))
#                result = c.fetchone()
#                if result is not None: # Check if the article is already in the database
#                    await client.send_message(message.channel, "Fehler - Artikel wurde schon vorgeschlagen")
#                    check = 5
#                    command_run = 1
#                    
#                if check == 0:
#                    datarow =(registered_name,args[1][pos1:length],1)
#                    # Insert the data into the SQLITE Table
#                    c.execute("INSERT INTO articles VALUES(?,?,?)", datarow)
#                    #member  = discord.utils.get(message.server.members, name=steem_name)
#                    #await client.send_message(member, "Wow - Ein Post von dir wurde von %s beim D-A-CH Support eingereicht!" % registered_name )
#                    db.commit()
#                    command_run = 1
#                    await client.send_message(message.channel, "Erfolg - Du hast einen Post von %s beim D-A-CH Support eingereicht!" % steem_name )
#                    
#        else:
#            await client.send_message(message.channel, "Fehler - Bitte den kompletten Link hinter §upvote einfügen, beginnend mit http...")

            
#    if message.content.upper().startswith("§CHECK"):
#        c.execute("SELECT * FROM meetup")
#        print("fetchall:")
#        result = c.fetchall() 
#        for r in result:
#            print(r)        
#        await client.send_message(message.channel, "Folgend Artikel sind derzeit eingereicht: /n %s " % result )
#        
        
    if message.content.upper().startswith("?ADDMEETUP"):
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":
                args = message.content.split(" ")
                Ort = str(args[1])
                Planer = str(args[2])
                Permlink = str(args[3])
                Datum = datetime.datetime.strptime(args[4], "%d.%m.%Y")
                #Datum = datetime.date(args[4])
                datarow =(Ort,Planer,Permlink,Datum)
                c.execute ("INSERT INTO meetup VALUES(?,?,?,?)", datarow )
                db.commit()
                command_run = 1
                executed = 1
                await client.send_message(message.channel, "Meetup von %s in %s wurde hinzugefügt" % (str(args[2]),str(args[1])) )
        if executed == 0:  
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
            command_run = 1
    
        
        
    if message.content.upper().startswith("?NEXTMEETUP"):
        default = 4
        if (len(message.content.strip()) > 11) and message.content[11] == " ":
            args = message.content.split(" ")
            if args[1].isdigit():
                default = args[1]
            
        c.execute("SELECT * FROM meetup ORDER BY date(\"datum\") ASC LIMIT (?)", (default,))
        #print("fetchall:")
        result = c.fetchall() 
        if len(result)==0:
            await client.send_message(message.channel, "Derzeit sind keine Meetups geplant" )
            command_run = 1
        else:
            today = datetime.datetime.today()
            for r in result: # building the informations per meetup to fill the embed and post the message in a nice format
                pos1 = r[2].find("@")
                pos2 = r[2].find("/",pos1)
                steemname = (r[2][pos1+1:pos2])
                sbd = s.get_account(steemname)
                picdest = (str(sbd["json_metadata"]))
                posanf = picdest.find("profile_image")
                posanf = posanf +16
                posend = picdest.find("\"",posanf)
                deltadays = r[3] - today
                daystomeetup = deltadays.days
                
                if deltadays.days >= -2:
                    if deltadays.days == 0:
                        daystomeetup = ("Morgen")
                    if deltadays.days == -1:
                        daystomeetup = ("Heute")
                    
                    embed = discord.Embed(title="Nächstes Meetup in: %s" % r[0], description="", color=0x00ff00)
                    embed.add_field(name="Planer", value="[%s](%s)" % (str(r[1]),"https://steemit.com/@"+str(r[1])))
                    embed.add_field(name="Link", value="[Link zum Steemit-Post](%s) " % str(r[2]), inline=True)
                    embed.add_field(name="Datum", value="%s" % datetime.datetime.strftime(r[3],"%d.%m.%Y"), inline=True)
                    embed.add_field(name="Tage bis zum Meetup", value="%s" % daystomeetup, inline=True)
                    embed.set_thumbnail(url=(picdest[posanf:posend]))
                    embed.timestamp=datetime.datetime.utcnow()
                    embed.set_footer(text="fresh from the DACH-BOT")
                    await client.send_message(message.channel, embed=embed)
                    command_run = 1
                else:
                    #await client.send_message(message.channel, "Derzeit sind keine Meetups geplant" )
                    command_run = 1
        
                
        
    if message.content.upper().startswith("?KILLMEETUP"): # Function to empty the table, only admins can do that, handle with care
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":
                c.execute("DELETE FROM meetup")
                db.commit()
                executed = 1
        if executed == 0:
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
        
                
        
    else:
        if message.content.upper().startswith("?") and command_run == 0 and len(message.content.strip()) > 2 :
            await printhelp(message)
        command_run =0           
client.run("your token here")
