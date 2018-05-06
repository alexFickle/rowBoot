import discord
client = discord.Client()

#needed for !pact and !frac
import time
start = time.time() #get the start time
import datetime
start_date = datetime.datetime.utcnow() # get the start date
#to find the current date/time : date = start_date + datetime.timedelta( seconds = (time.time() - start))

#import the passwords/ e-mail / master info for the bot, see private.py
import private
bot_email = private.bot_email
bot_password = private.bot_password
master = private.master


import urllib.request
import json
import re
numbersOnly = re.compile('[^\d]+')
import asyncio
fractalString = "" #stores the last given string so that unnecessary API calls are not done.
fractalStringDate = datetime.datetime(datetime.MINYEAR,1,1).isocalendar() #stores the date to see if the last API call occured in the same day.


@asyncio.coroutine
def fracCheck(date):
	global fractalStringDate
	global fractalString
	currentDate = date.isocalendar() #find current date, may be different then the date this function was last called during
	if currentDate == fractalStringDate:
		#if this function was called previously during the same day then fractalString is up to date.
		return fractalString #no API call needed
	print("API call needed") #debug/logging
	fractalStringDate = currentDate
	fractalString = "The Daily Recommended Fractals are: "
	with urllib.request.urlopen("https://api.guildwars2.com/v2/achievements/daily") as response:
		html = response.read()
	string = html.decode('utf-8') #string result from the api call
	obj = json.loads(string)
	idList = [] #the daily fractal achievement ids
	for element in obj["fractals"]:
		idList.append(element["id"])
	url = "https://api.guildwars2.com/v2/achievements?ids=" #url to be used to resolve achievment ids to names
	for id in idList :
		url+=str(id) + ','
	url = url[:-1]
	with urllib.request.urlopen(url) as response: 
		html = response.read()
	string = html.decode('utf-8') #string result from the api call
	obj = json.loads(string)
	for element in obj:
		if not "bits" in element:
			#the Daily Recommended N Achievement do not contain the key bits
			fractalString += numbersOnly.sub('',element["name"])
			fractalString += ", "
	for element in obj:
		if "bits" in element:
			#the Daily Tier N (Fractal Island Name) Achievements use the key bits
			include = True
			for bit in element["bits"]:
				if int(numbersOnly.sub('',bit["text"])) <= 75:
					include = False
			if include:
				fractalString += element["name"][13:]
				fractalString += ", "
	fractalString = fractalString[:-2] + '.'
	return fractalString


#used for !pact
pact_supply_network_locations = [
'[&BIkHAAA=] [&BC0AAAA=] [&BDoBAAA=] [&BO4CAAA=] [&BIUCAAA=] [&BCECAAA=]',
'[&BIcHAAA=] [&BKYBAAA=] [&BEwDAAA=] [&BNIEAAA=] [&BIMCAAA=] [&BA8CAAA=]',
'[&BH8HAAA=] [&BBkAAAA=] [&BEgAAAA=] [&BKgCAAA=] [&BGQCAAA=] [&BIMBAAA=]',
'[&BH4HAAA=] [&BKYAAAA=] [&BMIBAAA=] [&BP0CAAA=] [&BDgDAAA=] [&BPEBAAA=]',
'[&BKsHAAA=] [&BIMAAAA=] [&BE8AAAA=] [&BP0DAAA=] [&BF0GAAA=] [&BOcBAAA=]',
'[&BJQHAAA=] [&BNUGAAA=] [&BMMCAAA=] [&BJsCAAA=] [&BHsBAAA=] [&BNMAAAA=]',
'[&BH8HAAA=] [&BJIBAAA=] [&BLkCAAA=] [&BBEDAAA=] [&BEICAAA=] [&BBABAAA=]'
];

def reply(author, message, msg, talk):
	yield from client.send_message(message.channel,msg,tts=talk)

def join(author, message):
	if author.id == master:
		join_link = message.content.strip('!join ')
		print('attempting join: %s' % join_link ) #debug/logging
		yield from client.accept_invite(join_link)
		print('sucess!\n')#debug
		msg = "joined"
		yield from reply(author, message, msg, False)
	else:
		msg = "{0} can't tell me what to do".format(author)
		yield from reply(author, message, msg, False)

def test(author, message):
	print("test requst from {0} in {1}\n".format(author, message.channel)) #debug/logging
	print("id:{0}\n".format(author.id)) #used to find master_id in private.py
	msg = "Hello {0}.  Use !help for a list of commands".format(author)
	yield from reply(author, message, msg, False)
	
def leave(author, message):
	if author.id == master:
		print('leaving: %s' % message.server) #debug/logging
		msg = 'goodbye'
		yield from reply(author, message, msg, False)
		yield from client.leave_server(message.server)
	else:
		msg = 'no, you'
		yield from reply(author, message, msg, False)
		
@asyncio.coroutine
def frac(author, message,date):
	print('Fractal request received') #debug/logging
	msg = yield from fracCheck(date)
	print('%s\n' % msg) #debug
	yield from reply(author, message, msg, False)

def help(author, message):
	print("{0} needs some help\n".format(author)) #debug/logging
	msg = "Command list: !frac, !pact, !help, !test"
	yield from reply(author, message, msg, False)
	if author.id == master:
		msg = "Master only commands: !join, !fuck_off"
		yield from reply(author, message, msg, False)
		
def pact(author, message,date):
	print("Pact Supply Network Agent request received") #debug/logging
	print("Time: {0}:{1}:{2}".format(date.timetuple()[3],date.timetuple()[4],date.timetuple()[5])) #debug/logging
	daily_num = date.isocalendar()[2] - 1
	if date.timetuple()[3] > 8:
		daily_num = (daily_num + 1) % 7
	print("{0}: {1}\n".format(daily_num,pact_supply_network_locations[daily_num])) #debug/logging
	yield from reply(author, message, pact_supply_network_locations[daily_num], False)

def gameSet(author, message):
	if len(message.content) > 5:	
		yield from client.change_presence(game=discord.Game(name='NSA Recorder v2.3',url='www.nsa.gov',type=1))
	else:
		yield from client.change_presence(game=author.game)

def quit(author):
	if author.id == master:
		yield from client.change_presence(status=discord.Status.offline)
		yield from client.close()
	

@client.async_event
def on_message(message):
	author = message.author
	date = start_date + datetime.timedelta( seconds = (time.time() - start))
	if message.content.startswith('!test'):
		yield from test(author, message)
	elif message.content.startswith('!join'):
		yield from join(author, message)
	elif message.content.startswith('!fuck_off'): #you must be firm with the bot
		yield from leave(author, message)
	elif message.content.startswith('!frac'):
		yield from frac(author, message, date)
	elif message.content.startswith('!help'):
		yield from help(author, message)
	elif message.content.startswith('!pact'):
		yield from pact(author, message,date)
	elif message.content.startswith('!game'):
		yield from gameSet(author, message)
	elif message.content.startswith('!die'):
		yield from quit(author)

print("starting client\n") #debug
client.run(bot_email,bot_password)
