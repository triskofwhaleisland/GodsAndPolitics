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


##### Framework

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
        for usr in main['user_array']:
            print(main['users'][usr]['name'])
            if arg0.lower in main['users'][usr]['name'].lower():
                nationFound = [True, main['users'][usr].name]
                mentionID = usr

        if nationFound[0] and nationFound[1] != arg0:  # Loop back again to prioritize any exact matches
            for usr in main['user_array']:
                if main['users'][usr]['name'].lower() == arg0.lower():
                    nationFound = [True, main['users'][usr]['name']]
                    mentionID = usr

        if not nationFound[0]:
            usr = client.users[client.users.find(arg0)]
            if main['users'][userID]:
                userID = str(usr.id)
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
    return datetime.datetime(second=duration / 1000)


def hasRole(arg0_msg, arg1_role):
    return arg1_role in discord.Message.author.roles


def nextTurn(arg0_user):
    userID = main['users'][arg0_user]
    age = main['users'][arg0_user].technology_level - 1
    buildings = main['users'][arg0_user]['buildings']
    inventory = main['users'][arg0_user]['inventory']

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
    for i in range(buildings.industrial_complexes): userID.actions += random.randint(6, 10)
    # ^ Industrial Complexes (6-10 actions)

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
        nationalNews += f"\nA famine struck citizens of {userID.name}, resulting in {fatalities} fatalities."
    else:
        userID.population = math.ceil(userID.population * userID.pop_growth_modifier)
        inventory.food -= math.ceil(userID.population / 1_000_000)

    userID.initial_manpower = math.ceil(userID.population * userID.manpower_percentage)

    # Upkeep

    if math.ceil(userID.soldiers / 100) > userID.money:
        nationalNews += f"\nTroops in the {userID.name} deserted en masse. Analysts estimate up to 15% of their armed " \
                        f"forces and even colonists may have quite simply dissipated. "

        for i in range(len(config['units'])):
            userID['military'][config['units'][i]] = math.ceil(userID['military'][config['units'][i]] * 0.85)
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
    usr = main['users'][arg0_user]
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

            for x in range(len(main['province_array'])):
                if main['province_array'][x] == arg2_provs[i]:
                    province_taken = True

            if province_taken:
                prov_checks -= 1
            elif re.match('[a-zA-Z]', arg2_provs[i]) or int(arg2_provs[i]) > 849 or int(arg2_provs[i]) < 0:
                prov_checks -= 1
            else:
                prov_checks += 1

        if prov_checks == len(arg2_provs):
            for i in range(len(arg2_provs)):
                main['province_array'].append(arg2_provs[i])
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
    usr = main['users'][arg0_user]
    # "arquebusiers","musketmen","riflemen","infantry","modern_infantry","bombard","cannons","culverins",
    # "field_artillery","howitzers","armoured_cars","tanks","biplanes","bombers","fighters","strategic_bombers",
    # "galleons","men_of_war","ironclads","dreadnoughts","battleships","settlers","colonists","administrators"

    manpower_costs = [50_000, 50_000, 50_000, 50_000, 50_000, 20_000, 20_000, 20_000, 20_000, 20_000, 25_000, 25_000,
                      15_000, 15_000, 20_000, 20_000, 10_000, 20_000, 30_000, 50_000, 100_000, 100_000, 100_000, 50_000]
    quantity = [50_000, 50_000, 50_000, 50_000, 50_000, 500, 500, 500, 500, 500, 500, 500, 50, 50, 50, 50, 10, 10, 10,
                10, 10, 1, 1, 1]

    unit_exists = False
    unit_id = 0

    for i in range(len(config['units'])):
        if config['units'][i] == arg2_unit:
            unit_exists = True
            unit_id = i

    if unit_exists:
        if usr['military'][arg2_unit] >= arg3_amount:
            usr.soldiers -= math.ceil(manpower_costs[unit_id] / quantity[unit_id]) * arg3_amount
            usr.used_manpower -= math.ceil(manpower_costs[unit_id] / quantity[unit_id]) * arg3_amount
            usr['military'][arg2_unit] -= arg3_amount

            arg1_msg.channel.send(f"{arg3_amount} {arg2_unit} were disbanded. You were refunded " + math.ceil(
                manpower_costs[unit_id] / quantity[unit_id]) * arg3_amount + " manpower.")
        else:
            arg1_msg.channel.send(f"You don't have that many **{arg2_unit}**!")
    else:
        arg1_msg.channel.send("The type of unit that you have specified does not exist!")


def demolish(arg0_user, arg1_msg, arg2_building, arg3_amount):
    usr = main['users'][arg0_user]
    # "coal_mines", "gold_mines", "iron_mines", "lead_mines", "quarries", "farms", "lumberjacks", "refineries", "mines",
    # "workshops", "watermills", "factories", "industrial_complexes", "barracks", "artillery_factories", "auto_plants",
    # "aeroports", "dockyards"

    manpower_costs = [20000, 50000, 20000, 20000, 20000, 25000, 10000, 50000, 20000, 50000, 40000, 50000, 70000, 20000,
                      25000, 100000, 50000, 100000]

    building_exists = False
    building_id = 0

    for i in range(len(config['buildings'])):
        if config['buildings'][i] == arg2_building:
            building_exists = True
            building_id = i

    if building_exists:
        if usr["buildings"][arg2_building] >= arg3_amount:
            usr.used_manpower -= manpower_costs[building_id] * arg3_amount
            usr["buildings"][arg2_building] -= arg3_amount

            arg1_msg.channel.send(f"{arg3_amount} {arg2_building} were demolished. You were refunded "
                                  f"{manpower_costs[building_id] * arg3_amount} manpower, and {arg3_amount} "
                                  f"building slots were freed up.")
        else:
            arg1_msg.channel.send(f"You don't have that many **{arg2_building}**!")
    else:
        arg1_msg.channel.send("The type of building that you have specified does not exist!")

    updateBuildings(usr)


def mine(arg0_user, arg1_msg, arg2_actions):
    user_id = main['users'][arg0_user]
    inventory = main['users'][arg0_user]['inventory']
    mineable_materials = ["coal", "gold", "iron", "iron", "iron", "lead", "petrol", "stone", "stone"]

    resource_list = []
    out_of_actions = False

    if arg2_actions < 1000:
        for i in range(arg2_actions):
            if user_id.actions > 0:
                random_resource = random.choice(mineable_materials)
                user_id.actions -= 1
                inventory[random_resource] += 1
                resource_list.append(random_resource)
            else:
                out_of_actions = True
    else:
        arg1_msg.channel.send("The number you have specified is too large!")

    if arg1_msg != 'none':
        arg1_msg.channel.send(f"You dug up {', '.join(resource_list)} whilst on your mining haul.")
        if out_of_actions:
            arg1_msg.channel.send("You then proceeded to run out of actions.")


def forage(arg0_user, arg1_msg, arg2_actions):
    user_id = main['users'][arg0_user]
    inventory = main['users'][arg0_user]['inventory']

    salvaged_wood = 0
    out_of_actions = False

    if arg2_actions <= 1000:
        for i in range(arg2_actions):
            if user_id.actions > 0:
                user_id.actions -= 1
                inventory['wood'] += 1
                salvaged_wood += 1
            else:
                out_of_actions = True
    else:
        arg1_msg.channel.send("The number you have specified is too large!")

    if arg1_msg != 'none':
        arg1_msg.channel.send(f"You chopped {salvaged_wood} wood.")
        if out_of_actions:
            arg1_msg.channel.send("You then proceeded to run out of actions.")


def buy(arg0_user, arg1_msg, arg2_amount, arg3_type):
    if main['users'][arg0_user] is not None:
        user_id = main['users'][arg0_user]
        inventory = main['users'][arg0_user]['inventory']
        resource_list = [["coal", 1875], ["food", 2500], ["gold", 5000], ["iron", 3750], ["lead", 2000],
                         ["petrol", 5000], ["stone", 2500], ["wood", 2500]]

        resource_exists = False

        for i in range(len(resource_list)):
            if arg3_type == resource_list[i][0]:
                resource_exists = True
                if user_id.blockaded:
                    arg1_msg.channel.send("You can't buy items whilst blockaded!")
                else:
                    if user_id.money <= arg2_amount * resource_list[i][1]:
                        arg1_msg.channel.send(f"You don't have enough money to buy that much {resource_list[i][0]}!")
                    else:
                        arg1_msg.channel.send(f"You bought {arg2_amount} {arg3_type} "
                                              f"for M${arg2_amount * resource_list[i][1]}.")
                        user_id.money -= arg2_amount * resource_list[i][1]
                        inventory[arg3_type] += arg2_amount

        if not resource_exists and arg3_type != 'list':
            arg1_msg.channel.send("That resource isn't for sale!")


def sellGold(arg0_user, arg1_msg, arg2_actions):
    if main['users'][arg0_user] is not None:
        user_id = main['users'][arg0_user]
        inventory = main['users'][arg0_user]['inventory']
        auction_list = []
        out_of_gold = False

        if arg2_actions <= 1000:
            for i in range(arg2_actions):
                if inventory.gold > 0:
                    sold_for = random.randint(800, 1350)
                    inventory.gold -= 1
                    user_id.money += sold_for
                    auction_list.append(f'M${sold_for}')
                else:
                    out_of_gold = True
        else:
            arg1_msg.channel.send('The number you have specified is too large!')

        if not auction_list:  # auction list is empty: [] == False
            arg1_msg.channel.send("You don't even have gold!")
        else:
            arg1_msg.channel.send(f"You sold {arg2_actions} gold for {auction_list} on the auction block.")
            if out_of_gold:
                arg1_msg.channel.send("You then proceeded to run out of gold.")
    else:
        arg1_msg.channel.send("You don't even have a country!")


def sellPetrol(arg0_user, arg1_msg, arg2_actions):
    if main['users'][arg0_user] is not None:
        user_id = main['users'][arg0_user]
        inventory = main['users'][arg0_user]['inventory']
        auction_list = []
        out_of_petrol = False

        if arg2_actions <= 1000:
            for i in range(arg2_actions):
                if inventory.petrol > 0:
                    sold_for = random.randint(750, 1000)
                    inventory.petrol -= 1
                    user_id.money += sold_for
                    auction_list.append(f'M${sold_for}')
                else:
                    out_of_petrol = True
        else:
            arg1_msg.channel.send('The number you have specified is too large!')

        if not auction_list:  # auction list is empty: [] == False
            arg1_msg.channel.send("You don't even have petrol!")
        else:
            arg1_msg.channel.send(f"You sold {arg2_actions} petrol for {', '.join(auction_list)} on the auction block.")
            if out_of_petrol:
                arg1_msg.channel.send("You then proceeded to run out of gold.")
    else:
        arg1_msg.channel.send("You don't even have a country!")


def setGovernment(arg0_user, arg1_type):
    user_id = arg0_user
    user_id.government = arg1_type
    user_id['politics'][arg1_type] = 100
    if arg1_type == "absolute_monarchy":
        user_id.manpower_percentage = 0.05
        user_id.max_tax = 0.65
        user_id.civilian_actions_percentage = 0.10
    elif arg1_type == "constitutional_monarchy":
        user_id.manpower_percentage = 0.20
        user_id.max_tax = 0.35
        user_id.civilian_actions_percentage = 0.35
    elif arg1_type == "communism":
        user_id.manpower_percentage = 0.50
        user_id.max_tax = 0.05
        user_id.civilian_actions_percentage = 0.00
    elif arg1_type == "democracy":
        user_id.manpower_percentage = 0.25
        user_id.max_tax = 0.70
        user_id.civilian_actions_percentage = 0.50
    elif arg1_type == "fascism":
        user_id.manpower_percentage = 0.10
        user_id.max_tax = 0.70
        user_id.civilian_actions_percentage = 0.20


### Command functions

# randomElement => random.choice

# initVar never used


def updateBuildings(arg0_user):
    usr = arg0_user
    total_buildings = 0

    for i in range(len(config['buildings'])):
        total_buildings += usr['buildings'][config['buildings'][i]]

    usr.building_cap = usr.provinces * 5 + 10
    usr.building_count = total_buildings


def initUser(arg0_user):
    current_user = str(arg0_user)
    already_registered = False
    for usr in main['user_array']:
        if usr == current_user:
            already_registered = True

    # Customization

    if current_user not in main['users']: main['users'][current_user] = {}
    if 'name' not in main['users'][current_user]: main['users'][current_user]['name'] = ""
    if 'government' not in main['users'][current_user]: main['users'][current_user]['government'] = ""
    if 'technology_level' not in main['users'][current_user]: main['users'][current_user]['technology_level'] = 1
    if 'population' not in main['users'][current_user]: main['users'][current_user]['population'] = 2_000_0000

    if 'motto' not in main['users'][current_user]: main['users'][current_user]['motto'] = 'No motto set.'

    if 'initial_manpower' not in main['users'][current_user]:
        main['users'][current_user]['initial_manpower'] = 1_000_0000
    if 'manpower_percentage' not in main['users'][current_user]: main['users'][arg0_user]['manpower_percentage'] = 0.50
    if 'used_manpower' not in main['users'][current_user]: main['users'][current_user]['used_manpower'] = 0
    if 'soldiers' not in main['users'][current_user]: main['users'][current_user]['soldiers'] = 0

    if 'money' not in main['users'][current_user]: main['users'][current_user]['money'] = 10000
    if 'stability' not in main['users'][current_user]: main['users'][current_user]['stability'] = 75
    if 'coup_this_turn' not in main['users'][current_user]: main['users'][current_user]['coup_this_turn'] = False
    if 'overthrow_this_turn' not in main['users'][current_user]:
        main['users'][current_user]['overthrow_this_turn'] = False

    if 'news_this_turn' not in main['users'][current_user]: main['users'][current_user]['news_this_turn'] = ""

    # Modifiers
    if 'tax_rate' not in main['users'][current_user]: main['users'][current_user]['tax_rate'] = 0
    if 'max_tax' not in main['users'][current_user]: main['users'][current_user]['max_tax'] = 0
    if 'pop_available' not in main['users'][current_user]: main['users'][current_user]['pop_available'] = 0.5

    if 'production_buildings_modifier' not in main['users'][current_user]:
        main['users'][current_user]['production_buildings_modifier'] = 1
    if 'pop_growth_modifier' not in main['users'][current_user]: main['users'][current_user][
        'pop_growth_modifier'] = 1.0539

    if 'infamy' not in main['users'][current_user]: main['users'][current_user]['infamy'] = 0

    # Building cap
    if 'provinces' not in main['users'][current_user]: main['users'][current_user]['provinces'] = 0
    if 'building_count' not in main['users'][current_user]: main['users'][current_user]['building_count'] = 0
    if 'building_cap' not in main['users'][current_user]: main['users'][current_user]['building_cap'] = 10

    # Sub-objects
    if 'inventory' not in main['users'][current_user]: main['users'][current_user]["inventory"] = {}
    if 'buildings' not in main['users'][current_user]: main['users'][current_user]["buildings"] = {}
    if 'military' not in main['users'][current_user]: main['users'][current_user]["military"] = {}
    if 'politics' not in main['users'][current_user]: main['users'][current_user]["politics"] = {}

    # Crafting values
    if 'actions' not in main['users'][current_user]: main['users'][current_user]['actions'] = 10
    if 'civilian_actions' not in main['users'][current_user]: main['users'][current_user]['civilian_actions'] = 0
    if 'civilian_actions_percentage' not in main['users'][current_user]:
        main['users'][current_user]['civilian_actions_percentage'] = 0

    # Modifiers - only staff can set these
    if 'blockaded' not in main['users'][current_user]: main['users'][current_user].blockaded = False

    # Add all materials to inventory
    for material in config['materials']:
        if material not in main['users'][current_user]["inventory"]: main['users'][current_user]["inventory"][
            material] = 0

    # Add all political parties
    for government in governmentList:
        if government not in main['users'][current_user]["politics"]: main['users'][current_user]["politics"][
            government] = 0

    # Add all military units
    for unit in config['units']:
        if unit not in main['users'][current_user]["military"]: main['users'][current_user]["military"][unit] = 0

    if 'armies' not in main['users'][current_user]: main['users'][current_user]["armies"] = {}
    if 'army_array' not in main['users'][current_user]["armies"]: main['users'][current_user]["armies"][
        'army_array'] = []

    if 'last_election' not in main['users'][current_user]: main['users'][current_user].last_election = 0

    if not already_registered:
        main['user_array'].append(current_user)
        main['users'][current_user]['technology_level'] = 1
        main['users'][current_user]["inventory"]['food'] = 100
        main['users'][current_user]["buildings"]['workshops'] = 1
        main['users'][current_user]["military"]['settlers'] = 1

    # "Temp logic" (idk what that means, probably wrinkles out weird bugs
    if main['users'][current_user]['used_manpower'] < 0:
        main['users'][current_user]['used_manpower'] = 0
    elif main['users'][current_user]['used_manpower'] > main['users'][current_user]['manpower']:
        main['users'][current_user]['used_manpower'] = main['users'][current_user]['manpower']

    if main['users'][current_user]['soldiers'] < 0: main['users'][current_user]['soldiers'] = 0


### Army & Combat functions


def newArmy(arg0_user, arg1_msg, arg2_name):
    msg = arg1_msg
    name_exists = False

    if arg0_user in main['users']:
        if arg2_name != 'deleted_army':
            usr = main['users'][arg0_user]
            armies = main['users'][arg0_user]['armies']

            for army in armies['army_array']:
                if army == arg2_name:
                    name_exists = True

            if name_exists:
                msg.channel.send("There already exists an army by this name!")
            else:
                # Create the army
                armies['army_array'].append(arg2_name)
                armies[arg2_name] = {}
                armies[arg2_name]['name'] = arg2_name
                for unit in config['units']:
                    armies[arg2_name][unit] = 0
        else:
            msg.channel.send("Stop trying to cheese the system!")
    else:
        msg.channel.send("You don't have a country yet, you wannabe mercenary!")


def editArmy(arg0_user, arg1_msg, arg2_name, arg3_amount, arg4_unit, arg5_mode):
    msg = arg1_msg
    army = ''

    if arg0_user in main['users']:
        usr = main['users'][arg0_user]
        armies = main['users'][arg0_user]['armies']
        reserves = main['users'][arg0_user]['military']

        # Check if army exists (one match, not two like Vis's)

        for knownArmy in armies['army_array']:
            if knownArmy['name'].lower() == arg2_name.lower():
                army = knownArmy

        # Add units
        if army != 'deleted-army':
            # check if unit exists
            unit_exists = False
            for unit in config['units']:
                if unit == arg4_unit:
                    unit_exists = True

            if unit_exists:
                # Check for mode
                if arg5_mode == 'add':
                    if arg3_amount > reserves[arg4_unit]:
                        msg.channel.send("You don't have that many troops in reserve!")
                    else:
                        armies[army][arg4_unit] += arg3_amount
                        reserves[arg4_unit] -= arg3_amount

                        msg.channel.send(f"**{arg3_amount}** {arg4_unit} were deployed"
                                         f"in the {armies[army]['name']}.")
                elif arg5_mode == 'remove':
                    if arg3_amount > armies[army][arg4_unit]:
                        msg.channel.send(f"You don't have that many troops in {armies[army]['name']}!")
                    else:
                        armies[army][arg4_unit] -= arg3_amount
                        reserves[arg4_unit] += arg3_amount

                        msg.channel.send(f"You placed **{arg3_amount}** {arg4_unit}"
                                         f"from the {armies[army]['name']} back into reserve.")
                else:
                    msg.channel.send(f'{arg5_mode} is not a valid operation!')
            else:
                msg.channel.send("The unit you have specified doesn't exist!")
        else:
            msg.channel.send("The army you have specified doesn't exist!")
    else:
        msg.channel.send("You don't have a country yet, you wannabe mercenary!")


def renameArmy(arg0_user, arg1_msg: discord.Message, arg2_name: str, arg3_newname):
    msg = arg1_msg
    if arg0_user in main['users']:
        usr = main['users'][arg0_user]
        armies = main['users'][arg0_user]['armies']
        army = ''
        for knownArmy in armies['army_array']:
            if armies[knownArmy]['name'].lower() == arg2_name.lower():
                army = knownArmy
                break
        if army:
            old_name = armies[army]['name']
            armies[army]['name'] = arg3_newname
            msg.channel.send(f"You have updated the name of the {old_name} to the **{arg3_newname}**!")
        else:
            msg.channel.send("The army you have specified is nonexistent!")
    else:
        msg.channel.send("You're stateless!")


def deleteArmy(arg0_user, arg1_msg: discord.Message, arg2_name):
    msg = arg1_msg

    if arg0_user in main['users']:
        usr = main['users'][arg0_user]
        armies = main['users'][arg0_user]['armies']
        army = ''
        for knownArmy in armies['army_array']:
            if armies[knownArmy]['name'].lower() == arg2_name.lower():
                army = knownArmy
                break

        if army != 'deleted-army':
            old_name = armies[army]['name']
            for unit in config['units']:
                usr['military'][unit] += armies[army][unit]
                armies[army][unit] = 0

            armies[army]['name'] = 'deleted-army'
            msg.channel.send(f"You have demobilised the **{old_name}**! They have now been returned to the reserves.")
        else:
            msg.channel.send("The army you have specified is nonexistent!")
    else:
        msg.channel.send("You're currently stateless!")


def printArmy(arg0_user, arg1_msg, arg2_name):
    msg = arg1_msg

    if arg0_user in main['users']:
        usr = main['users'][arg0_user]
        armies = main['users'][arg0_user]['armies']
        army = ''
        for knownArmy in armies['army_array']:
            if armies[knownArmy]['name'].lower() == arg2_name.lower():
                army = knownArmy
                break

        if army != 'deleted-army':
            ap_units = [1, 2, 5, 6, 10, 1000, 1500, 2500, 10000, 15000, 3000, 10000, 2000, 5000, 1000, 25000, 1000,
                        2500, 7000, 10000, 20000, 0, 0, 0]
            dp_units = [1, 2, 5, 8, 10, 300, 300, 500, 200, 500, 6000, 20000, 2000, 1000, 10000, 5000, 1000, 2500, 5000,
                        20000, 10000, 0, 0, 0]

            ap = sum([armies[army][config['ground_units'][i]] * ap_units[i] for i in range(len(config['units']))])
            dp = sum([armies[army][config['ground_units'][i]] * dp_units[i] for i in range(len(config['units']))])

            military_string = [f":bust_in_silhouette: User: {arg0_user.name}",
                               f":map: Country: {main['users'][arg0_user].name}",
                               f"------------------ \n:crossed_swords: **{armies[army]['name']}**:",
                               "------------------",
                               ]
            military_string.extend(
                [f":guard: **{config['ground_units'][i]}**: {armies[army][config['ground_units'][i]]}"
                 for i in range(len(config['ground_units'])) if armies[army][config['ground_units'][i]] > 0]
            )
