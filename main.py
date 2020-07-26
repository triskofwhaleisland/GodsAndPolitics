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

    ### Politics

    # Stability and revolt risk

    stab_tax_rate = userID.tax_rate * 100
    stab_party_popularity = userID['politics'][userID.government]
    if userID.government not in ['communism', 'fascism', 'dictatorship', 'monarchy']:
        stab_government_modifier = 5
    else:
        stab_government_modifier = -5

    userID.stability = math.ceil(stab_party_popularity + stab_government_modifier - math.ceil(stab_tax_rate))

    if random.randint(0, 100) > userID.stability + 30 or userID.coup_this_turn:
        userID.tax_rate = 0
        new_government = governmentList[(governmentList.index(userID.government) + 1) % len(governmentList)]
        setGovernment(userID, new_government)

        nationalNews += f"The country of {userID.name} fell into a state of civil unrest, allowing supporters of " \
                        f"{userID.government} to coup the government!\n Rioters then went on strike, leading the " \
                        f"country of {userID.name} to lose all their actions!\n"
        userID.coup_this_turn = False
        userID.actions = 0

    if userID.overthrow_this_turn:
        userID.tax_rate = 0
        new_government = governmentList[
            (governmentList.index(userID.government) - 1 + len(governmentList) % len(governmentList))]
        setGovernment(userID, new_government)

        nationalNews += f"The country of {userID.name} fell into a state of civil unrest, leading supporters of " \
                        f"{userID.government} to coup the government!\n Rioters then went on strike, leading the " \
                        f"country of {userID.name} to lose all their actions!\n"
        userID.overthrow_this_turn = False
        userID.actions = 0

    # Civilian Actions
    userID.civilian_actions = math.ceil(userID.actions * userID.civilian_actions_percentage)

    nationalNews += f"\nThe country of {userID.name} now has {userID.actions} actions, of which" \
                    f"{(math.ceil(userID.civilian_actions * 0.5) + math.ceil(userID.civilian_actions * 0.5))}" \
                    f"were automatically used by the populace."

    mine(arg0_user, 'non', math.ceil(userID.civilian_actions * 0.5))
    forage(arg0_user, 'non', math.ceil(userID.civilian_actions * 0.5))

    news.append(nationalNews)


def settle(arg0_user, arg1_msg, arg2_provs):
    usr = main.users[arg0_user]
    provs = arg2_provs
    prov_checks = 0
    has_unit = False
    unit_type = ""

    if len(arg2_provs) == 1:
        if usr.military.settlers > 0:
            has_unit = True
            unit_type = 'settlers'
            usr.soldiers -= 200_000
            usr.used_manpower -= 200_000
    elif len(arg2_provs) == 3:
        if usr.military.settlers > 0:
            has_unit = True
            unit_type = 'colonists'
            usr.soldiers -= 100_000
            usr.used_manpower -= 100_000
    elif len(arg2_provs) == 5:
        if usr.military.settlers > 0:
            has_unit = True
            unit_type = 'administrators'
            usr.soldiers -= 50_000
            usr.used_manpower -= 50_000

    if has_unit:
        for i in range(len(arg2_provs)):
            province_taken = False

            for x in range(len(main.province_array)):
                if main.province_array[x] == arg2_provs[i]:
                    province_taken = True

            if province_taken:
                prov_checks -= 1
            elif re.match('[a-zA-Z]', arg2_provs[i]) or int(arg2_provs[i]) > 849 or int(arg2_provs[i]) < 0:
                prov_checks -= 1
            else:
                prov_checks += 1

        if prov_checks == len(arg2_provs):
            for i in range(len(arg2_provs)):
                main.province_array.append(arg2_provs[i])
                usr.provinces += 1
            usr.military[unit_type] -= 1

            arg1_msg.channel.send(f"Settlers from **{usr.name}** colonised the province(s) of {', '.join(arg2_provs)}."
                                  f"They now have **{usr.provinces}** provinces. "
                                  f"\n<@213287117017710593> EXPANSION ALERT!")
        else:
            arg1_msg.channel.send("One of the provinces you have specified turned out to be invalid!")
    else:
        arg1_msg.channel.send("You have specified an invalid amount of arguments!")

    updateBuildings(usr)


def disband(arg0_user, arg1_msg, arg2_unit, arg3_amount):
    usr = main.users[arg0_user]
    # "arquebusiers","musketmen","riflemen","infantry","modern_infantry","bombard","cannons","culverins",
    # "field_artillery","howitzers","armoured_cars","tanks","biplanes","bombers","fighters","strategic_bombers",
    # "galleons","men_of_war","ironclads","dreadnoughts","battleships","settlers","colonists","administrators"

    manpower_costs = [50_000, 50_000, 50_000, 50_000, 50_000, 20_000, 20_000, 20_000, 20_000, 20_000, 25_000, 25_000,
                      15_000, 15_000, 20_000, 20_000, 10_000, 20_000, 30_000, 50_000, 100_000, 100_000, 100_000, 50_000]
    quantity = [50_000, 50_000, 50_000, 50_000, 50_000, 500, 500, 500, 500, 500, 500, 500, 50, 50, 50, 50, 10, 10, 10,
                10, 10, 1, 1, 1]

    unit_exists = False
    unit_id = 0

    for i in range(config.units.length):
        if config.units[i] == arg2_unit:
            unit_exists = True
            unit_id = i

    if unit_exists:
        if usr['military'][arg2_unit] >= arg3_amount:
            usr.soldiers -= math.ceil(manpower_costs[unit_id] / quantity[unit_id]) * arg3_amount
            usr.used_manpower -= math.ceil(manpower_costs[unit_id] / quantity[unit_id]) * arg3_amount
            usr['military'][arg2_unit] -= arg3_amount

            arg1_msg.channel.send(f"{arg3_amount} {arg2_unit} were disbanded. You were refunded " + Math.ceil(
                manpower_costs[unit_id] / quantity[unit_id]) * arg3_amount + " manpower.")
