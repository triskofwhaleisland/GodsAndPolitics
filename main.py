import datetime
import discord
import json

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
startDate = datetime.date(2020, 7, 26)
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
    eval(open('config.txt').readlines())

readConfig()

help = open('help.txt')