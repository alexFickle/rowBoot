import discord
client = discord.Client()

#needed for !pact and !frac
import time
start = time.time() #get the start time (ctime)
import datetime
start_date = datetime.datetime.utcnow() # get the start date
#to find the current date/time : date = start_date + datetime.timedelta( seconds = (time.time() - start))

#import the passwords/ e-mail / master info for the bot, see private.py
import private
bot_email = private.bot_email
bot_password = private.bot_password
master = private.master

#used for !frac
frac_list = [ 
'Solid Ocean, Underground Facility, Urban Battleground',
'Aetherblade, Thaumanova Reactor, Molten Furnace',
'Cliffside, Molten Boss, Captain Mai Trin Boss',
'Swampland, Solid Ocean, Uncategorized',
'Aquatic Ruins, Snowblind, Thaumanova Reactor',
'Aetherblade, Uncategorized, Volcanic',
'Cliffside, Urban Battleground, Chaos Isles',
'Underground Facility, Volcanic, Captain Mai Trin Boss',
'Snowblind, Solid Ocean, Swampland',
'Chaos Isles, Uncategorized, Urban Battleground',
'Cliffside, Molten Furnace, Captain Mai Trin Boss',
'Underground Facility, Thaumanova Reactor, Molten Boss',
'Volcanic, Swampland, Aetherblade',
'Snowblind, Chaos Isles, Aquatic Ruins'
];


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

def frac(author, message,date):
	print('Fractal request received') #debug/logging
	print("Time: {0}:{1}:{2}".format(date.timetuple()[3],date.timetuple()[4],date.timetuple()[5])) #debug/logging
	print("Week: {0}, Day of Week: {1}".format(date.isocalendar()[1],date.isocalendar()[2])) #debug/logging
	daily_num = date.isocalendar()[2] - 1 + ((date.isocalendar()[1] % 2) * 7)
	print("{0}: {1}".format(daily_num, frac_list[daily_num])) #debug/logging
	msg = 'The daily fractals are %s.' % frac_list[daily_num]
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
		yield from frac(author, message,date)
	elif message.content.startswith('!help'):
		yield from help(author, message)
	elif message.content.startswith('!pact'):
		yield from pact(author, message,date)
		
print("beep boop\n") #debug
client.run(bot_email,bot_password)
