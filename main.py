# RankedBot
# Version: 2.2
# Date: 10.10.21
# Current Authors: fury#1662, fingers_#5020
# fingers making the improvements!
# Github: https://github.com/furyaus/rankbot
# Repl.it: https://replit.com/@furyaus/rankbot
# Original Author: Mazun19 from the PUBG community
# Original Date: 2019

import discord, requests, json, os, datetime, asyncio, traceback
import stats as playerStatistics
from discord.ext import commands, tasks
from operator import itemgetter
from datetime import timedelta
from pytz import timezone

# Setup bot and command
clientintents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=clientintents)
client.remove_command("help")

# Global variables
users_file = "users.json"
data_file = "data.json"
fingersraw_file = "fingersdata.json"
curr_season = "division.bro.official.pc-2018-12"
prev_season = "division.bro.official.pc-2018-11"
prev_prev_season = "division.bro.official.pc-2018-10"
bot_token = os.environ['discord_token']
API_key_fury = os.environ['API_key_fury']
API_key_ocker = os.environ['API_key_ocker']
API_key_p4 = os.environ['API_key_p4']
API_key_progdog = os.environ['API_key_progdog']
API_key_fingers = os.environ['API_key_fingers']
d_server = int(os.environ['discord_server'])
debugmode = int(os.environ['debug']) #New debug mode added, if this is 1 it'll message to the channels for the looped status updates
announce_channel = int(os.environ['announce_channel'])
botstats_channel = int(os.environ['botstats_channel'])
stats_channel = int(os.environ['stats_channel'])
stats_msg = int(os.environ['stats_msg'])
general_channel = int(os.environ['general_channel'])
error_channel = int(os.environ['error_channel'])
botinfo_channel = int(os.environ['botinfo_channel'])
botinfo_msg = int(os.environ['botinfo_msg'])
botlog_channel = int(os.environ['botlog_channel'])
top25ranks_channel = int(os.environ['top25ranks_channel'])
top25ranks_msg = int(os.environ['top25ranks_msg'])
top25kda_channel = int(os.environ['top25kda_channel'])
top25kda_msg = int(os.environ['top25kda_msg'])
top25adr_channel = int(os.environ['top25adr_channel'])
top25adr_msg = int(os.environ['top25adr_msg'])
streaming_role = int(os.environ['streaming_role'])
admin_roles = ["Moderators", "Admin", "Boss", "The General", "The Punisher", "The Terminator",]
no_requests = 0
curr_key = 0
loop_timer = 0.05 #0.05 is 5 minutes #0.005 is 30 seconds

# Keys in order - furyaus, ocker, p4, progdog, fingers
keys = ["Bearer " + API_key_fury, "Bearer " + API_key_ocker, "Bearer " + API_key_p4, "Bearer " + API_key_progdog, "Bearer " + API_key_fingers]
header = {"Authorization": "Bearer " + API_key_fury,"Accept": "application/vnd.api+json"}


# Standard bot reponse message embed format

def helpmsg(titleText=None,descText=None):
    if(titleText==None and descText==None):
        help_msg = discord.Embed(colour=discord.Colour.orange())
    if(titleText!=None and descText==None):
        help_msg = discord.Embed(colour=discord.Colour.orange(),title=titleText)
    if(titleText==None and descText!=None):
        help_msg = discord.Embed(colour=discord.Colour.orange(),description=descText)
    if(titleText!=None and descText!=None):
        help_msg = discord.Embed(colour=discord.Colour.orange(),title=titleText,description=descText)
    help_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    return help_msg


def respmsg(titleText=None,descText=None):
    if(titleText==None and descText==None):
        response_msg = discord.Embed(colour=discord.Colour.orange())
    if(titleText!=None and descText==None):
        response_msg = discord.Embed(colour=discord.Colour.orange(),title=titleText)
    if(titleText==None and descText!=None):
        response_msg = discord.Embed(colour=discord.Colour.orange(),description=descText)
    if(titleText!=None and descText!=None):
        response_msg = discord.Embed(colour=discord.Colour.orange(),title=titleText,description=descText)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    return response_msg

# Open user list and load into arrray
def get_data(file):
    with open(file, "r") as file:
        return json.loads(file.read())

# Close user list and store in JSON file
def set_data(file, data, comment):
    with open(file, 'w') as file:
        print('update to {0} because {1}'.format(file.name,comment))
        json.dump(data, file, indent=2)

# Catch unknown commands
@client.event
async def on_command_error(ctx, error):
    response_msg = respmsg()
    response_msg.add_field(name="Error",value=f"An error occured: {str(error)}",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Let admin know about errors
@client.event
async def on_error(event, *args, **kwargs):
    channel = client.get_channel(error_channel)
    response_msg = respmsg()
    response_msg.description = event
    response_msg.add_field(name='Event', value='```py\n%s\n```' % traceback.format_exc())
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# Help
@client.command()
async def help(ctx):

    response_msg = respmsg("Help for Rank Bot","Rank Bot manages the roles, ranks and other stats for gamers in The 101 Club.")
    response_msg.add_field(name=".link",value="This links your discord userid with your PUBG in-game name. ```.link furyaus```",inline=False)
    response_msg.add_field(name=".stats",value="Retireve live PUBG API data for a single user and display. No stats, ranks or roles are changed or stored. ```.stats 0cker```",inline=False)
    response_msg.add_field(name=".mystats",value="Queries PUBG API for your latest data, updates ranks, roles and stats which are stored via a JSON file. ```.mystats```",inline=False)
    response_msg.add_field(name=".inspire",value="Responses with inspiration quotes, to really get you back on track for that chicken dinner.```.inspire```",inline=False)
    response_msg.add_field(name="Report issues",value="Head to github and create a new issue or feature request [https://github.com/furyaus/rankbot/issues](https://github.com/furyaus/rankbot/issues)",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)


# Admin help
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def adminhelp(ctx):

    response_msg = respmsg("Admin help for Rank Bot","Admin users can remove users and call for global updates.")
    response_msg.add_field(name=".linked",value="Returns the total number of currently stored users in JSON file. ```.linked```",inline=False)
    response_msg.add_field(name=".say",value="Allows admin to message any channel. Can take channel name or channel ID. Look out for icons when using channel name. 1024 character limit. ```.say channel_name message```",inline=False)
    response_msg.add_field(name=".announce",value="Allows admin to send a announcement to the announcement channel only. 1024 character limit. ```.announce message```",inline=False)
    response_msg.add_field(name=".norequests",value="Returns the total number of requests made to the PUG API. ```.norequests```",inline=False)
    response_msg.add_field(name=".userinfo",value="Caculates the creation date and join date of user for 101 Club. ```.userinfo GAMMB1T```",inline=False)
    response_msg.add_field(name=".ban",value="Bans a user and logs why into the bot-log channel. ```.ban 0cker Because he sucks```",inline=False)
    response_msg.add_field(name=".unban",value="Unbans a user and direct messages them to rejoin via invite. ```.unban 0cker```",inline=False)
    response_msg.add_field(name=".remove",value="Will allow admin to remove link between Discord user id and PUBG IGN. User can then complete a link again. ```.remove @P4```",inline=False)
    response_msg.add_field(name=".resync",value="This will force a full resync for all stored players with PUBG API. 50 users per minute, wait till complete. ```.resync```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)


# Inspire your day
@client.command()
async def inspire(ctx):
    response_msg = respmsg()
    request = requests.get("https://leksell.io/zen/api/quotes/random")
    json_data = json.loads(request.text)
    quote = json_data['quote'] + " -" + json_data['author']
    if request.status_code != 200:
        request = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(request.text)
        quote = json_data[0]['q'] + " -" + json_data[0]['a']
    response_msg.add_field(name="Quote", value=quote, inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Say
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def say(self, channel: discord.TextChannel=None, *, message):
    response_msg = respmsg()
    response_msg.add_field(name="Rank Bot says", value=message, inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# announce
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def announce(ctx, *, text):
    channel = client.get_channel(announce_channel)
    response_msg = respmsg()
    response_msg.add_field(name="Announcement", value=f"{text}", inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# Report how many users in JSON file
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def linked(ctx):
    user_list=get_data(users_file)
    response_msg = respmsg()
    response_msg.add_field(name="Users linked",value="```" + str(len(user_list)) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Report number of PUBG API requests
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def norequests(ctx):
    response_msg = respmsg()
    response_msg.add_field(name="PUG API Requests",value="```" + str(no_requests) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Remove user from JSON file
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def remove(ctx, member: discord.Member):
    user_list=get_data(users_file)
    response_msg = respmsg()
    try: 
        del user_list[str(member.id)]
        set_data(users_file, user_list,'remove users')
    except:
        pass
    response_msg.add_field(name="Removed",value="```" + str(member.name) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Remove user from JSON when they leave server and report
@client.event
async def on_member_remove(member):
    user_list=get_data(users_file)
    channel = client.get_channel(botlog_channel)
    response_msg = respmsg()
    try: 
        del user_list[str(member.id)]
        set_data(users_file, user_list, 'on member remove')
        response_msg.add_field(name="Left server", value=f"{member.name} was removed from user list in rank data.", inline=False)
    except:
        response_msg.add_field(name="Left server", value=f"{member.name} was not in user list for rank data.", inline=False)
        pass
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)


# On member join add role and report
@client.event
async def on_member_join(member):
    guild = client.get_guild(d_server)
    channel = client.get_channel(botlog_channel)
    await discordAddRole('101 Club',member)
    response_msg = respmsg()
    response_msg.add_field(name="Server join", value=f"{member.name}", inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

#Target user add exception handling
async def grabTargetUser(user):
    guild = client.get_guild(d_server)
    member = None
    try:
        print('Fetching member info for {0}'.format(user))
        member = await guild.fetch_member(user)
    except:
        print('Error occured getting member info for {0}'.format(user))
    return member

# Standard role add a remove function
async def discordRemoveRole(targetRole, user, ctx=None):
    if ctx == None:
        guild = client.get_guild(d_server)
        role = discord.utils.get(guild.roles, name=targetRole)
    else:
        role = discord.utils.get(ctx.guild.roles, name=targetRole)
    await user.remove_roles(role)

async def discordAddRole(targetRole, user, ctx=None):
    if ctx == None:
        guild = client.get_guild(d_server)
        role = discord.utils.get(guild.roles, name=targetRole)
    else:
        role = discord.utils.get(ctx.guild.roles, name=targetRole)
    await user.add_roles(role)

async def discordRemoveAndAddRole(removeRole,targetRole,user, ctx=None):
    await discordRemoveRole(removeRole,user,ctx)
    await discordAddRole(targetRole,user,ctx)

async def discordReplaceRole(targetRole, olduser, newuser, ctx=None):
    if ctx == None:
        guild = client.get_guild(d_server)
        role = discord.utils.get(guild.roles, name=targetRole)
    else:
        role = discord.utils.get(ctx.guild.roles, name=targetRole)
    await discordRemoveRole(role,olduser,ctx)
    await discordAddRole(role,newuser,ctx)

# Streaming Role
@client.event
async def on_member_update(before, after):
    guild = client.get_guild(d_server)
    streaming_role = discord.utils.get(guild.roles, name='Streaming')
    after_id = after.id
    member = await grabTargetUser(after_id)
    streaming = [i for i in after.activities if str(i.type) == "ActivityType.streaming"]
    if streaming:
        if streaming_role not in after.roles:
            print(f"{after.display_name} is streaming")
            await discordAddRole('Streaming',member)
    else:
        if streaming_role in after.roles:
            print(f"{after.display_name} is not streaming")
            await discordRemoveRole('Streaming',member)
            

# Ban function
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def ban(ctx, member:discord.User=None, *, reason=None):
    channel = client.get_channel(botlog_channel)
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    if reason == None:
        reason = "For being a jerk!"
    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await member.send(message)
    response_msg = respmsg()
    response_msg.add_field(name="Member banned", value=f"{member.name}", inline=False)
    response_msg.add_field(name="Reason", value=reason, inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)
    await ctx.send(embed=response_msg)

# Unban function
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def unban(ctx, member:commands.MemberConverter):
    channel = client.get_channel(botlog_channel)
    response_msg = respmsg()
    banned_users = await ctx.guild.bans()
    if member.id in banned_users:
        await ctx.guild.unban(member.id)
        message2 = f"You have been unbanned from {ctx.guild.name}. Please rejoin - [https://discord.gg/the101club](https://discord.gg/the101club)"
        response_msg.add_field(name="Member unbanned", value=member.name, inline=False)
        await member.send(message2)
    else:
        response_msg.add_field(name="Not found", value="Name is not currently in ban list.", inline=False)
    await channel.send(embed=response_msg)
    await ctx.send(embed=response_msg)

# Server stats
@tasks.loop(hours=loop_timer)
async def serverstats():
    guild = client.get_guild(d_server)
    channel = client.get_channel(stats_channel)
    user_list=get_data(users_file)
    data_list = get_data(data_file)
    no_requests = data_list['no_requests']
    newmessage = False
    try:
        message = await channel.fetch_message(stats_msg)
    except:
        newmessage = True
        print("Couldn't find {0} message in {1} channel.".format(stats_msg, stats_channel))
    response_msg = respmsg()
    response_msg.add_field(name="Users",value="Number of 101 Club members: ```" + str(guild.member_count)+ "```",inline=False)
    response_msg.add_field(name="Channels",value="Number of channels in the 101 Club: ```" + str(len(guild.channels)) + "```",inline=False)
    response_msg.add_field(name="Sync completed",value="PUGB API requests completed: ```" + str(no_requests) + "```",inline=False)
    response_msg.add_field(name="Tracked ranked players",value="```" + str(len(user_list)) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    if(newmessage == True):
        print('Posting a new message in stats')
        await channel.send(embed=response_msg)
    else:
        print('Editing the message in stats')
        await message.edit(embed=response_msg)

# User discord stats
@client.command()
async def userinfo(ctx, member: discord.Member):
    created_at = member.created_at.strftime("%b %d, %Y")
    joined_at = member.joined_at.strftime("%b %d, %Y")
    roles = ''
    for role in member.roles:
       if str(role) != '@everyone':
          roles = roles+"\n"+str(role)
    response_msg = respmsg("User info for "+member.name)
    response_msg.add_field(name="Created", value=f"{member.name} was created on "+created_at, inline=False)
    response_msg.add_field(name="Joined", value=f"{member.name} joined 101 Club on "+joined_at, inline=False)
    response_msg.add_field(name="Roles", value=f"{member.name} has the following roles: "+roles, inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)


# User def
def updateUserList(user_list, user_id, user_ign, player_id, playerStats, curr_punisher=0, curr_terminator=0, curr_general=0):
    user_list.update({str(user_id): {'IGN': user_ign,'ID': player_id,'Rank': playerStats.pStats.new_rank}})
    user_list[str(user_id)]['c_rank'] = playerStats.pStats.c_rank
    user_list[str(user_id)]['c_tier'] = playerStats.pStats.c_tier
    user_list[str(user_id)]['c_rank_points'] = playerStats.pStats.c_rank_points
    user_list[str(user_id)]['h_rank'] = playerStats.pStats.h_rank
    user_list[str(user_id)]['h_tier'] = playerStats.pStats.h_tier
    user_list[str(user_id)]['h_rank_points'] = playerStats.pStats.h_rank_points
    user_list[str(user_id)]['games_played'] = playerStats.pStats.games_played
    user_list[str(user_id)]['season_wins'] = playerStats.pStats.season_wins
    user_list[str(user_id)]['KDA'] = playerStats.pStats.KDA
    user_list[str(user_id)]['ADR'] = playerStats.pStats.ADR
    user_list[str(user_id)]['punisher'] = curr_punisher
    user_list[str(user_id)]['terminator'] = curr_terminator
    user_list[str(user_id)]['general'] = curr_general
    user_list[str(user_id)]['team_kills'] = playerStats.pStats.team_kills
    return user_list

# Top 25 Updates
@tasks.loop(hours=loop_timer)
async def top25update():
    print('Starting top 25 update')
    user_list=get_data(users_file)
    reportTypeMessage = ''
    reportTypes = ['ADR', 'KDA', 'c_rank_points']
    message = ''
    for reportType in reportTypes:
        newmessage = False
        if(reportType=='c_rank_points'):
            channel = client.get_channel(top25ranks_channel)
            await debugmessage(channel, 'starting rank channel work')
            try:
                message = await channel.fetch_message(top25ranks_msg)
            except:
                newmessage = True
                await debugmessage(channel, "{0} exception occurred couldn't find {1} message.".format(reportType, top25ranks_msg))
            reportTypeMessage = 'rank'
            reportTypeStats = 'Rank'
        elif(reportType=='KDA'):
            channel = client.get_channel(top25kda_channel)
            await debugmessage(channel, 'starting kda channel work')
            try:
                message = await channel.fetch_message(top25kda_msg)
            except:
                newmessage = True
                await debugmessage(channel, "{0} exception occurred couldn't find {1} message.".format(reportType, top25kda_msg))
            reportTypeMessage = 'KDA'
            reportTypeStats = 'KDA'
        elif(reportType=='ADR'):
            channel = client.get_channel(top25adr_channel)
            await debugmessage(channel, 'starting adr channel work')
            try:
                message = await channel.fetch_message(top25adr_msg)
            except:
                newmessage = True
                await debugmessage(channel, "{0} exception occurred couldn't find {1} message.".format(reportType, top25adr_msg))
            reportTypeMessage = 'ADR'
            reportTypeStats = 'ADR'
        else:
            break
        new_user_list = sorted(user_list.values(), key=itemgetter(reportType))
        response_msg = respmsg("Top 25 {0} holders in the 101 Club".format(reportTypeMessage))
        top_string = ''
        i = -1
        total_length = len(new_user_list)
        j = 1 
        while i > -(total_length+1):
            ign = new_user_list[i]['IGN']
            player_stats = new_user_list[i][reportType]
            players = new_user_list[i][reportTypeStats] 
            curr_line = "%i : %s, %s, %.0f\n" % (abs(j), ign,players,player_stats)
            top_string += curr_line
            j += 1
            if j == 26:
                break
            i -= 1
        response_msg.add_field(name="Top {0} holders:".format(reportTypeMessage), value="```"+top_string+"```",inline=False)
        response_msg.timestamp = datetime.datetime.utcnow()
        #If there is an exception getting them message post a new message otherwise edit the message.
        if(newmessage == True):
            print('Posting a new message')
            await channel.send(embed=response_msg)
        else:
            print('Editing the message in top25 '+reportType)
            await message.edit(embed=response_msg)
        print("top25 {0} updated".format(reportTypeMessage))

# Check my stats - live, direct api data response - allows any PUBG IGN
@client.command(aliases=['rank'])
async def stats(ctx, user_ign):
    global keys
    global header
    global no_requests
    data_list = get_data(data_file)
    no_requests = data_list['no_requests']
    user_list=get_data(users_file)
    user_ign = user_ign.replace("<", "")
    user_ign = user_ign.replace(">", "")
    user_ign = user_ign.replace("@", "")
    user_ign = user_ign.replace("!", "")
    for user in user_list:
        if (user == user_ign):
            user_ign = user_list[user]['IGN']
    response_msg = respmsg("Stats for " + user_ign)
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    #Consolidated IGN parts into single def
    initial_r = await playerIgn(curr_header, user_ign)
    if initial_r.status_code != 200:
        response_msg.add_field(name="Error",value="Incorrect PUBG IGN (case sensitive) or PUBG API is down.",inline=False)
    else:
        player_info = json.loads(initial_r.text)
        player_id = str(player_info['data'][0]['id'].replace('account.', ''))
        #Consolidated playerInfo in a def
        second_request = await playerInfo(player_id, curr_header)
        if(player_id=="329883909338824715"):
            set_data(fingersraw_file,second_request,"Dumping fingers data to review")
        #Added all session infor to a new playerStats class
        playerStats = playerStatistics.statsCalc(player_id,second_request)
        response_msg.add_field(name="Rank",value=f"Current rank is: {playerStats.pStats.c_rank} {playerStats.pStats.c_tier}: {playerStats.pStats.c_rank_points}\nHighest rank is: {playerStats.pStats.h_rank} {playerStats.pStats.h_tier}: {playerStats.pStats.h_rank_points}",inline=False)
        response_msg.add_field(name="KDA",value=f"Kills and assists per death: {playerStats.pStats.KDA}",inline=False)
        response_msg.add_field(name="ADR",value=f"Average damage per game: {playerStats.pStats.ADR}",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)
    data_list['no_requests'] = no_requests
    set_data(data_file, data_list, 'stats')

# Link Discord user id with PUBG IGN and create user
@client.command()
async def link(ctx, user_ign):
    global keys
    global header
    global no_requests
    user_list=get_data(users_file)
    data_list = get_data(data_file)
    no_requests = data_list['no_requests']
    response_msg = respmsg("Linking " + user_ign)
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in user_list:
        response_msg.add_field(name="Issue",value="Your IGN has already been added to the list, just use .mystats to update your rank",inline=False)
    else:
        #Consolidated IGN parts into single def
        initial_r = await playerIgn(curr_header, user_ign)
        if initial_r.status_code != 200:
            response_msg.add_field(name="Issue",value="Incorrect PUBG IGN (case sensitive) or PUBG API is down.",inline=False)
        else:
            player_info = json.loads(initial_r.text)
            player_id = str(player_info['data'][0]['id'].replace('account.', ''))
            #Consolidated playerInfo in a def
            second_request = await playerInfo(player_id, curr_header)
            #Added all session infor to a new playerStats class
            playerStats = playerStatistics.statsCalc(player_id,second_request)
            #Def to update all user information from stats class
            user_list = updateUserList(user_list, user_id, user_ign, player_id, playerStats)
            await discordAddRole(playerStats.pStats.new_rank,user, ctx)
            response_msg.add_field(name="Rank",value=f"Current rank is: {playerStats.pStats.c_rank} {playerStats.pStats.c_tier}: {playerStats.pStats.c_rank_points}\nHighest rank is: {playerStats.pStats.h_rank} {playerStats.pStats.h_tier}: {playerStats.pStats.h_rank_points}",inline=False)
            response_msg.add_field(name="Done",value="Discord linked with PUBG IGN and stats saved to file.",inline=False)
    set_data(users_file, user_list, 'link')
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Confirm legitmate PUBG IGN
async def playerIgn(curr_header, user_ign):
    global no_requests
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
    request = requests.get(url, headers=curr_header)
    no_requests += 1
    if request.status_code == 429:
        print('Too many API requests, sleep 60secs')
        await asyncio.sleep(60)
        curr_header['Authorization'] = keys[no_requests % (len(keys))]
        request = requests.get(url, headers=curr_header)
        no_requests += 1
    return request

# Collect player ranked season data  
async def playerInfo(player_id, curr_header):
    global no_requests
    season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    request = requests.get(season_url, headers=curr_header)
    no_requests += 1
    if request.status_code == 429:
        print('Too many API requests, sleep 60secs')
        await asyncio.sleep(60)
        curr_header['Authorization'] = keys[no_requests % (len(keys))]
        request = requests.get(season_url, headers=curr_header)
        no_requests += 1
    season_info = json.loads(request.text)
    return season_info

# Set secert debug variable to 1 for extra messages
async def debugmessage(ctx,message):
    if(debugmode == 1):
        await ctx.send(message)


# Pull stats for current user and update database
@client.command()
async def mystats(ctx):
    global keys
    global header
    global no_requests
    user_list = get_data(users_file)
    data_list = get_data(data_file)
    no_requests = data_list['no_requests']
    channel = client.get_channel(botstats_channel)
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    response_msg = respmsg("Stats for " + user.name)
    await debugmessage(channel, 'got user id {0}'.format(user_id))
    if str(user_id) in user_list:
        curr_rank = user_list[str(user_id)]['Rank']
        curr_terminator = user_list[str(user_id)]['terminator']
        curr_punisher = user_list[str(user_id)]['punisher']
        curr_general = user_list[str(user_id)]['general']
        #convert player_id to string
        player_id = str(user_list[str(user_id)]['ID'])
        user_ign = user_list[str(user_id)]['IGN']
        #Consolidated playerInfo in a def
        second_request = await playerInfo(player_id, curr_header)
        #Added all session infor to a new playerStats class
        playerStats = playerStatistics.statsCalc(player_id, second_request)
        await debugmessage(channel, 'got player stats for id {0}'.format(player_id))
        #Def to update all user information from stats class
        user_list = updateUserList(user_list, user_id, user_ign, player_id, playerStats, curr_punisher, curr_terminator, curr_general)
        if playerStats.pStats.new_rank != curr_rank:
            await discordRemoveAndAddRole(curr_rank, playerStats.pStats.new_rank, user, ctx)
        response_msg.add_field(name="Rank", value=f"Current rank is: {playerStats.pStats.c_rank} {playerStats.pStats.c_tier}: {playerStats.pStats.c_rank_points}\nHighest rank is: {playerStats.pStats.h_rank} {playerStats.pStats.h_tier}: {playerStats.pStats.h_rank_points}", inline=False)
        response_msg.add_field(name="KDA",value=f"Kills and assists per death: {playerStats.pStats.KDA}", inline=False)
        response_msg.add_field(name="ADR",value=f"Average damage per game: {playerStats.pStats.ADR}", inline=False)
        response_msg.add_field(name="Done",value=f"Updated stats and saved to file.", inline=False)
    else:
        response_msg.add_field(name="Rank",value=f"You currently don't have a rank and your IGN isn't added to the list so use .link command to link",inline=False)
    set_data(users_file, user_list, 'update')
    await debugmessage(channel, 'setting user data for {0}'.format(player_id))
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)
    data_list['no_requests'] = no_requests
    set_data(data_file, data_list, 'update')
    await debugmessage(channel, 'setting data call for {0}'.format(player_id))

# Main program - full resync all data, ranks, roles and stats
@tasks.loop(hours=1.0)
async def update():
    global keys
    global header
    global no_requests
    aest = timezone('Australia/Melbourne')
    timestamp = datetime.datetime.now(aest)
    user_list=get_data(users_file)
    data_list = get_data(data_file)
    no_requests = data_list['no_requests']
    guild = client.get_guild(d_server)
    channel = client.get_channel(botinfo_channel)
    newmessage = False
    try:
        message = await channel.fetch_message(botinfo_msg)
    except:
        newmessage = True
        print("Couldn't find {0} message in {1} channel.".format(botinfo_msg, botinfo_channel))
    response_msg = respmsg("Sync all data for The 101 Club")
    curr_header = header
    for user in user_list:
        player_id = str(user_list[user]['ID'])
        user_ign = user_list[user]['IGN']
        curr_rank = user_list[user]['Rank']
        curr_terminator = user_list[user]['terminator']
        curr_punisher = user_list[user]['punisher']
        curr_general = user_list[user]['general']
        #Consolidated playerInfo in a def
        request = await playerInfo(player_id, curr_header)
        #Added all session infor to a new playerStats class
        playerStats = playerStatistics.statsCalc(player_id, request)
        #Def to update all user information from stats class
        user_list_na = updateUserList(user_list, user, user_ign, player_id, playerStats, curr_punisher, curr_terminator, curr_general)
        if playerStats.pStats.new_rank != curr_rank:
            role = discord.utils.get(guild.roles, name=curr_rank)
            member = await grabTargetUser(user)
            if(member != None):
                await discordRemoveAndAddRole(curr_rank,playerStats.pStats.new_rank,member)
    
    user_list = user_list_na

    #############################################################
    # Bittne off more then I can chew here, I want to revist this role part and make it easier use less code for each
    # Ahh I feel like that every time I work on any project, that is currently working but at the same time
    # I want it to be more optimsed and better!!!
    #############################################################
    # unique_member_titles = ['The General','The Terminator','The Punisher']
    #Default each title to None
    # current_general = 'None'
    # current_terminator = 'None'
    # current_punisher = 'None'
    # targetstat = ''
    # targetwords = ''
    # for title in unique_member_titles:
    #     #General work
    #     if(title=='The General'):
    #         max_points = 0
    #         max_points_user = ''
    #         for user in user_list:
    #             if user_list[user]['general'] == 1:
    #                 current_general = user
    #         for user in user_list:
    #             if (user_list[user]['c_rank_points'] > max_points):
    #                 max_points = user_list[user]['c_rank_points']
    #                 max_points_user = user
    #         user_list[max_points_user]['general'] = 1
    #         targetstat = 'general'
    #         targetwords = 'General'
        
    #     if current_general == 'None':
    #         member = await guild.fetch_member(max_points_user)
    #         await discordAddRole(title,member,guild)
    #         response_msg.add_field(name=title,value=f"A new {0} role (highest rank) has been assigned. Congrats! {1}".format(title,member.name),inline=False)
    #     elif current_general == max_points_user:
    #         member = await guild.fetch_member(current_general)
    #         response_msg.add_field(name=title,value=f"{0} is the same as before. {1}".format(title,member.name),inline=False)
    #     else:
    #         oldmember = await guild.fetch_member(current_general)
    #         user_list[current_general]['general'] = 0
    #         newmember = await guild.fetch_member(max_points_user)
    #         await discordReplaceRole(title,oldmember,newmember,guild)
    #         response_msg.add_field(name=title,value=f"Previous {0} (highest rank) has been replaced. Congrats! {1}".format(targetwords,newmember.name),inline=False)
    #Added updated list back to original
    
    max_points = 0
    max_points_user = ''
    current_general = 'None'
    for user in user_list:
        if user_list[user]['general'] == 1:
            current_general = user
    for user in user_list:
        if (user_list[user]['c_rank_points'] > max_points):
            max_points = user_list[user]['c_rank_points']
            max_points_user = user
    user_list[max_points_user]['general'] = 1
    
    if current_general == 'None':
        member = await grabTargetUser(max_points_user)
        if member != None:
            await discordAddRole('The General',member,guild)
            response_msg.add_field(name="The General",value=f"A new The General role (highest rank) has been assigned. Congrats! ```{member.name}```",inline=False)
    elif current_general == max_points_user:
        member = await grabTargetUser(current_general)
        if member != None:
            response_msg.add_field(name="The General",value=f"The General is the same as before. ```{member.name}```",inline=False)
    else:
        oldmember = await grabTargetUser(current_general)
        user_list[current_general]['general'] = 0
        newmember = await grabTargetUser(max_points_user)
        if oldmember != None and newmember != None:
            await discordReplaceRole('The General',oldmember,newmember,guild)
            response_msg.add_field(name="The General",value=f"Previous General (highest rank) has been replaced. Congrats! ```{newmember.name}```",inline=False)

    max_kda = 0
    max_kda_user = ''
    current_terminator = 'None'
    for user in user_list:
        if user_list[user]['terminator'] == 1:
            current_terminator = user
    for user in user_list:
        if (user_list[user]['KDA'] > max_kda):
            max_kda = user_list[user]['KDA']
            max_kda_user = user
    user_list[max_kda_user]['terminator'] = 1
    #Terminator work
    if current_terminator == 'None':
        member = await grabTargetUser(max_kda_user)
        await discordAddRole('The Terminator',member)
        if member != None:
            response_msg.add_field(name="The Terminator",value=f"A new The Terminator role (highest KDA) has been assigned. Congrats! ```{member.name}```",inline=False)
    elif current_terminator == max_kda_user:
        member = await grabTargetUser(max_kda_user)
        if member != None:
            response_msg.add_field(name="The Terminator",value=f"The Terminator is the same as before. ```{member.name}```",inline=False)
    else:
        oldmember = await grabTargetUser(current_terminator)
        user_list[current_terminator]['terminator'] = 0
        newmember = await grabTargetUser(max_kda_user)
        if oldmember != None and newmember != None:
            await discordReplaceRole("The Terminator",oldmember,newmember)
            response_msg.add_field(name="The Terminator",value=f"Previous Terminator (highest KDA) has been replaced. Congrats! ```{member.name}```",inline=False)

    max_adr = 0
    max_adr_user = ''
    current_punisher = 'None'
    for user in user_list:
        if user_list[user]['punisher'] == 1:
            current_punisher = user
    for user in user_list:
        if (user_list[user]['ADR'] > max_adr):
            max_adr = user_list[user]['ADR']
            max_adr_user = user
    user_list[max_adr_user]['punisher'] = 1
    #Punished work
    if current_punisher == 'None':
        member = await grabTargetUser(max_adr_user)
        await discordAddRole("The Punisher",member,guild)
        if member != None:
            response_msg.add_field(name="The Punisher",value=f"A new The Punisher role (highest ADR) has been assigned. Congrats! ```{member.name}```",inline=False)
    elif current_punisher == max_adr_user:
        member = await grabTargetUser(max_adr_user)
        if member != None:
            response_msg.add_field(name="The Punisher",value=f"The Punisher is the same as before. ```{member.name}```",inline=False)
    else:
        oldmember = await grabTargetUser(current_punisher)
        user_list[current_punisher]['punisher'] = 0
        newmember = await grabTargetUser(max_adr_user)
        if oldmember != None and newmember != None:
            await discordReplaceRole("The Terminator",oldmember,newmember,guild)
            response_msg.add_field(name="The Punisher",value=f"Previous Punisher (highest ADR) has been replaced. Congrats! ```{member.name}```",inline=False)

    response_msg.add_field(name="Sync completed",value="PUGB API requests completed: ```" + str(no_requests) + "```",inline=False)
    response_msg.add_field(name="Users linked",value="```" + str(len(user_list)) + "```",inline=False)
    response_msg.add_field(name="Finished",value=f"All player stats, ranks, roles have been updated. The next sync will take place at "+((timestamp+ timedelta(hours=1)).strftime(r"%I:%M %p")),inline=False)
    print('Updated everyones stats')
    set_data(users_file, user_list, 'update everyone stats')
    response_msg.timestamp = datetime.datetime.utcnow()
    if(newmessage == True):
        print('Posting a new message in bot-info')
        await channel.send(embed=response_msg)
    else:
        print('Editing the message in bot-info')
        await message.edit(embed=response_msg)
    data_list['no_requests'] = no_requests
    set_data(data_file, data_list, 'update everyone stats')

# Resync all
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def resync(ctx):
    response_msg = respmsg()
    response_msg.add_field(name="Resync started",value="This could take a long time based on the number of users and the PUBG API, please wait for the comfirmation message before more commands. 50 users per minute is our limit.",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)
    await update()
    await top25update()
    response_msg = respmsg()
    response_msg.add_field(name="Resync completed",value="PUGB API requests completed: ```" + str(no_requests) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# main
@client.event
async def on_ready():
    update.start()
    top25update.start()
    serverstats.start()

# Run the bot
client.run(bot_token)