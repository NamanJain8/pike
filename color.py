import json

color = {
	"ID"	:	"red",
	"NUMBER":	"green",
	"RESERVED":	"yellow"
}

with open('color_config.json','w+') as f:
	json.dump(color,f)