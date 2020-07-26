import datetime
import json
import math
import random
import re

import discord

with open('config.json') as config:
    prefix, token = json.load(config).values()

client = discord.Client()


@client.event
async def on_ready():
    print('[GodsAndPolitics] is ready. Hello!')


client.login(token)

'''

TYPES OF UNITS

Infantry
Artillery
Cavalry/Tanks
Battleships/Aircraft Carriers
Submarines/Nuclear Submarines

Fighters/Multirole Fighters
Bombers/Strategic Bombers

'''

# Bot settings

botPrefix = '$'  # TODO fix references to prefix
startDate = datetime.datetime(2020, 7, 26, 18, 0, 0)
turnTimer = 60
announcementsChannel = 695628446738546740
authorizedRole = ""

governmentList = ["absolute_monarchy", "constitutional_monarchy", "communism", "democracy", "fascism"]

config = {
    'materials': ["coal", "food", "gold", "iron", "lead", "petrol", "stone", "wood"],
    'buildings': ["coal_mines", "gold_mines", "iron_mines", "lead_mines", "quarries", "farms", "lumberjacks",
                  "refineries", "mines", "workshops", "watermills", "factories", "industrial_complexes", "barracks",
                  "artillery_factories", "auto_plants", "aeroports", "dockyards"],
    'units': ["arquebusiers", "musketmen", "riflemen", "infantry", "modern_infantry", "bombard", "cannons", "culverins",
              "field_artillery", "howitzers", "armoured_cars", "tanks", "biplanes", "bombers", "fighters",
              "strategic_bombers", "galleons", "men_of_war", "ironclads", "dreadnoughts", "battleships", "settlers",
              "colonists", "administrators"],
    'visible_units': ["arquebusiers", "musketmen", "riflemen", "infantry", "modern_infantry", "bombard", "cannons",
                      "culverins", "field_artillery", "howitzers", "armoured_cars", "tanks", "biplanes", "bombers",
                      "fighters", "strategic_bombers", "galleons", "men_of_war", "ironclads", "dreadnoughts",
                      "battleships", "settlers", "colonists", "administrators"],

    'ground_units': ["arquebusiers", "musketmen", "riflemen", "infantry", "modern_infantry"],
    'ground_artillery': ["bombard", "cannons", "culverins", "field_artillery", "howitzers"],
    'ground_vehicles': ["armoured_cars", "tanks"],
    'aeroplanes': ["biplanes", "bombers", "fighters", "strategic_bombers"],
    'naval_units': ["galleons", "men_of_war", "ironclads", "dreadnoughts", "battleships"],
    'colonists': ["settlers", "colonists", "administrators"]
}

main = json.load(open('database.js'))


def readConfig():
    eval(open('config.txt').read())


readConfig()


def prepFile(filename, replace=False):
    with open(filename) as f:
        rawText = f.read() if not replace else f.read().replace('@', botPrefix)
    text = []
    if len(rawText) >= 2000:
        while len(rawText) >= 2000:
            text.append(rawText[:2000])
            rawText = rawText[2000:]
    else:
        text = [rawText]
    return text


helpText = prepFile('help.txt')
buildCosts = prepFile('build_costs.txt')
unitCosts = prepFile('unit_costs.txt')
governments = prepFile('governments.txt')
cb = prepFile('casus_belli.txt')
itemCosts = prepFile('item_costs.txt')

user = ''
botInput = ''

building_list = []
news = []


### Framework

# Operating Functions

# randomNumber => random.randint


def saveConfig():
    botSettings = [
        f'bot_prefix = "{botPrefix}"',
        'start_date = datetime.datetime(2020, 7, 26, 18, 0, 0)',
        f'turn_timer = {turnTimer}',
        f'announcements_channel = "{announcementsChannel}"',
    ]
    with open('config.txt', 'w') as f:
        try:
            f.write('\n'.join(botSettings))
        except OSError as e:
            print(e)


def equalsIgnoreCase(arg0, arg1):
    return arg0.lower() == (botPrefix + arg1).lower()


def returnMention(arg0):
    userExists = False

    if re.match('^[A-Za-z]+$', arg0):
        print('Alphanumeric string used!')
        mentionID = ''
        nationFound = [False, '']
        userID = ''
        for user in main.user_array:
            print(main.users[user].name)
            if main.users[user].name.lower().indexOf(arg0.lower()) != -1:
                nationFound = [True, main.users[user].name]
                mentionID = user

        if nationFound[0] and nationFound[1] != arg0:  # Loop back again to prioritize any exact matches
            for user in main.user_array:
                if main.users[user].name.lower() == arg0.lower():
                    nationFound = [True, main.users[user].name]
                    mentionID = user

        if not nationFound[0]:
            user = client.users[client.users.find(arg0)]
            if main.users[userID]:
                userID = str(user.id)
                userExists = True
        else:
            return mentionID

        print(nationFound)
    else:
        mentionID = arg0.replace(re.compile('(<)(@)(!)'), '').replace('(<)(@)', '').replace('>', '')
        return mentionID

    if userExists:
        return userID


def returnChannel(arg0):
    return client.get_channel(arg0)


def parseMilliseconds(duration):
    return datetime.datetime(duration * 1000)


def hasRole(arg0_msg, arg1_role):
    return arg1_role in discord.Message.author.roles


def nextTurn(arg0_user):
    userID = main.users[arg0_user]
    age = main.users[arg0_user].technology_level - 1
    buildings = main.users[arg0_user]['buildings']
    inventory = main.users[arg0_user]['inventory']

    # News variables:

    nationalNews = ''

    famineLoss = math.ceil(userID.population * 0.1)

    ### Building income

    # Actions production
    userID.actions += 5

    for i in range(buildings.mines): userID += 1  # Mines (1 action)
    for i in range(buildings.workshops): userID.actions += random.randint(2, 3)  # Workshops (2-3 actions)
    for i in range(buildings.watermills): userID.actions += random.randint(3, 5)  # Watermills (3-5 actions)
    for i in range(buildings.factories): userID.actions += random.randint(5, 7)  # Factories (5-7 actions)
    for i in range(buildings.industrial_complexes): userID.actions += random.randint(6,
                                                                                     10)  # Industrial Complexes (6-10 actions)

    # Raw resource production

    inventory.coal += (buildings.coal_mines * 3)
    inventory.gold += (buildings.gold_mines * 1)
    inventory.iron += (buildings.iron_mines * 3)
    inventory.lead += (buildings.lead_mines * 3)
    inventory.stone += (buildings.quarries * 5)

    inventory.food += (buildings.farms * 5)
    inventory.wood += (buildings.lumberjacks * 5)
    inventory.petrol += (buildings.refineries * 5)

    # Population

    userID.money += math.ceil((userID.actions * 2500) * userID.tax_rate)
    userID.pop_growth_modifier = 1.0285

    # Food

    if userID.population > userID['inventory'].food * 1_000_000:
        fatalities = 0
        if userID.government == 'communism':
            fatalities = math.ceil(userID.population * 0.095)  # 9.5% population penalty for inadequate food
        else:
            fatalities = math.ceil(userID.population * 0.065)  # 6.5% population penalty for inadequate food
        userID.population -= fatalities
        nationalNews += f"\nA famine struck citizens of {user_id.name}, resulting in {fatalities} fatalities."
    else:
        userID.population = math.ceil(userID.population * userID.pop_growth_modifier)
        inventory.food -= math.ceil(userID.population / 1_000_000)

    userID.initial_manpower = math.ceil(userID.population * userID.manpower_percentage)

    # Upkeep

    if math.ceil(userID.soldiers / 100) > userID.money:
        nationalNews += f"\nTroops in the {userID.name} deserted en masse. Analysts estimate up to 15% of their armed " \
                        f"forces and even colonists may have quite simply dissipated. "

        for i in range(len(config.units)):
            userID['military'][config.units[i]] = math.ceil(userID['military'][config.units[i]] * 0.85)
            userID.used_manpower -= userID.soldiers * 0.15
            userID.soldiers *= 0.85

    # Politics
