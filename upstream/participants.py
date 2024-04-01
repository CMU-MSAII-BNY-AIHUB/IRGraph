import json
from schema import *
from neo4j import GraphDatabase


# URI = "neo4j+s://b38f7a62.databases.neo4j.io"
# AUTH = ("neo4j", "v58CFsyXYfGg7TxCLWUD41IegFELmo5x8WpwvKcjZbc")

# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     driver.verify_connectivity()

    
with open('/home/cehong/Desktop/Capstone/AuraDB/data/global_speaker.json', 'r') as file:
    json_input = file.read()
    
data = json.loads(json_input)
# Create a list to hold the person objects
persons = []

# Iterate over each item in the data dictionary to create Person objects
for name, info in data.items():
    print(name, info)
    breakpoint()
    person = Person(id=info['id'], 
                    position=info['position'], 
                    group=info['company'], 
                    name=info['name'])
    persons.append(person)

# Print the created Person objects
for person in persons:
    print(person)


# driver.close()