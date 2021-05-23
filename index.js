const Discord = require("discord.js");
const bot = new Discord.Client();
const config = require("./config.json");
const prefix = config.prefix;
const botname = "QuarGen";
const prefix1 = "+";
var fs = require("fs");
var lineReader = require("line-reader");
var async = require("async");
const firstline = require("firstline");
const generated = new Set();
var os = require("os");
var express = require('express');
var app = express();
const chalk = require('chalk');

  bot.on('ready', msg => {             
	console.log(`Global statistics : \n\nThe bot has a total of ${bot.guilds.cache.size} Servers. \nFor a total of ${bot.users.cache.size} Members.`)
	console.log("Logged in as " + bot.user.id + " | Prefix : " + prefix1 + " | Number of Servers "+ bot.guilds.cache.size +" | Number of lounges "+ bot.channels.cache.size +" | Utilisateur totaux "+ bot.users.cache.size +" | Nombre d'emojis totaux "+ bot.emojis.cache.size +'');
	bot.user.setActivity("+help - QuarGen");
});

bot.on("message", message => {
    if (message.channel.type != 'dm') {//message.channel.id === config.botChannel) { 
        if (message.author.bot) return;
        var command = message.content
            .toLowerCase()
            .slice(prefix.length)
            .split(" ")[0];

        if (command === "gen") {
            if (generated.has(message.author.id)) {
                const embed = {
                        title: "Oops!",
                        description: "Cooldown Still Active! \n(30 Seconds For VIP)\n (0 miliseconds For Premium)\n (1 Minute For Normal)",
                        color: 0xff033d,
                        timestamp: new Date(),
						author: {
							name: botname + " - account generator",
							url: "https://discord.gg/DekcZ9xMud",
						icon_url: bot.displayAvatarURL
						},
                        fields: []
                    };
                message.channel.send({ embed });
            } else {
                let messageArray = message.content.split(" ");
                let args = messageArray.slice(1);
                if (!args[0])
                    return message.reply("Please provide a service!");
                var fs = require("fs");
                const filePath = __dirname + "/comptes/" + args[0] + ".txt";

                const embed = {
                    title: "Out of stock!",
                    description: "The service you requested is currently out of stock!",
                    color: 0xff033d,
                    timestamp: new Date(),
                    author: {
                        name: botname + " - account generator",
                        url: "https://discord.gg/DekcZ9xMud",
                        icon_url: bot.displayAvatarURL
                    },
                    fields: []
                };

                fs.readFile(filePath, function (err, data) {
                    if (!err) {
                        data = data.toString();
                        var position = data.toString().indexOf("\n");
                        var firstLine = data.split("\n")[0];
                        if(position == -1)
                        return message.channel.send({ embed });
					    const embed = {
                                    title: "Account " + args[0] + " generated!",
                                    description: firstLine,
                                    color: 0xff033d,
                                    timestamp: new Date(),
							author: {
								name: botname + " - account generator",
								url: "https://discord.gg/DekcZ9xMud",
								icon_url: bot.displayAvatarURL
							},
							fields: []
                        };
                        message.author.send({ embed });
                        if (position != -1) {
                            data = data.substr(position + 1);
                            fs.writeFile(filePath, data, function (err) {
                                const embed = {
                                    title: "Account " + args[0] + " generated!",
                                    description: "The account for your requested service has been sent as DM!",
                                    color: 0xff033d,
                                    timestamp: new Date(),
									author: {
										name: botname + " - account generator",
										url: "https://discord.gg/DekcZ9xMud",
										icon_url: bot.displayAvatarURL
									},
                                    fields: []
                                };
                                message.channel.send({ embed });
								if (message.channel.id === config.prem) {
									console.log(message.author.name + " Has prem!")
								} else if (message.channel.id === config.vip) {
									generated.add(message.author.id);
									setTimeout(() => {generated.delete(message.author.id);},30000);
									if (err) {
										console.log(err);
									}
								} else {
									generated.add(message.author.id);
									setTimeout(() => {generated.delete(message.author.id);},60000);
									if (err) {
										console.log(err);
									}
								}});
                        } else {
                            message.channel.send("Out of stock!");
                        }
                    } else {
                        const embed = {
                            title: "Service not found!",
                            description: "The requested service cannot be found!",
                            color: 0xff033d,
                            timestamp: new Date(),
                  	  author: {
                        	name: botname + " - account generator",
           	             url: "https://discord.gg/DekcZ9xMud",
                	        icon_url: bot.displayAvatarURL
                   	 },
                            fields: []
                        };
                        message.channel.send({ embed });
                        return;
                    }
                });
            }
        }
        else
            if (command === "stats") {
                const embed = {
                    title: "Stats " + botname,
                    description: "Total number of users: `" + bot.users.cache.size + " membres`\nTotal number of rooms: `" + bot.channels.cache.size+ " salons`\nTotal number of emoji: `" + bot.emojis.cache.size+ " émojis`\nTotal number of servers: `" + bot.guilds.cache.size+ " server(s)`",
                    color: 0xff033d,
                    timestamp: new Date(),
                    author: {
                        name: botname + " - account generator",
                        url: "https://discord.gg/DekcZ9xMud",
                        icon_url: bot.displayAvatarURL
                    },
                    fields: []
                };
                message.channel.send({ embed });
            }
	
            if (command === "stock") {
                const embed = {
                    title: "Our Current Stock!",
                    description: "Realtime Stock Counter",
                    color: 0xff033d,
                    timestamp: new Date(),
                    author: {
                        name: botname + " - account generator",
                        url: "https://discord.gg/DekcZ9xMud",
                        icon_url: bot.displayAvatarURL
                    },
                    fields: [
					    {
                            name: 'Disney+ [1]',
                            value: "Example: `" + prefix1 + "gen disney+`",
                        },
						{
                            name: 'Nitro-Unchecked [10k]',
                            value: "Example: `" + prefix1 + "gen nitro-unchecked`",
                        },
						{
                            name: 'Netflix [0]',
                            value: "Example: `" + prefix1 + "gen netflix`",
                        },
						{
                            name: 'NordVPN [58]',
                            value: "Example: `" + prefix1 + "gen nordvpn`",
                        },
						{
                            name: 'Proxies [1155]',
                            value: "Example: `" + prefix1 + "gen proxies`",
                        },
						{
                            name: 'Spotify [0]',
                            value: "Example: `" + prefix1 + "gen spotify`",
                        },
						{
                            name: 'Steam [34]',
                            value: "Example: `" + prefix1 + "gen steam`",
                        },
					]
                };
                message.channel.send({ embed });
            }
			
            if (command === "help") {

                const embed = {
                    color: 0xff033d,
                    title: botname + ' - account generator',
                    url: 'https://discord.gg/j6w2dtwyBG',
                    author: {
                        name: 'List of commands',
                        url: 'https://discord.gg/DekcZ9xMud',
                    },

                    description: '**This is a list of all orders**',
                    fields: [
                        {
                            name: 'Generate accounts',
                            value: "Example: `" + prefix1 +"gen <Service name>`",
                        },
                        {
                            name: 'Create a service',
                            value: "Example: `" + prefix1 +"create <Service name>`",
                        },
                        {
                            name: 'Notify account restocks',
                            value: "Example: `" + prefix1 +"restock <Service name> <Number of accounts>`",
                        },
                        {
                            name: 'Add accounts',
                            value: "Example: `" + prefix1 +"add <mail:pass> <Service name>`",
                        },
                        {
                            name: 'View bot statistics ' + botname,
                            value: "Example: `" + prefix1 +"stats`",
                        },
                    ],
                    timestamp: new Date(),
                };
                message.channel.send({ embed });
            }

        if (command === "add") {
            if (!message.member.hasPermission("ADMINISTRATOR"))
                return message.reply("You don't have the permissions to do this!");
            var fs = require("fs");
            let messageArray = message.content.split(" ");
            let args = messageArray.slice(1);
            var account = args[0]
            var service = args[1]
            if(!account) return message.reply("Provide a formatted account string first!")
            if(!service) return message.reply("Provide service first!")
            const filePath = __dirname + "/comptes/" + args[1] + ".txt";
            fs.appendFile(filePath, os.EOL + args[0], function (err) {
                if (err) return console.log(err);
                const embed = {
                    title: "Account added!",
                    description: "Account successfully added to `" + service + "`!",
                    color: 0xff033d,
                    timestamp: new Date(),
                    author: {
                        name: botname + " - account generator",
                        url: "https://discord.gg/DekcZ9xMud",
                        icon_url: bot.displayAvatarURL
                    },
                    fields: []
                };
                message.channel.send({ embed });
            });


        }	
        if (command === "create") {
            if (!message.member.hasPermission("ADMINISTRATOR"))
                return message.reply("You don't have the permissions to do this!");
            var fs = require("fs");
            let messageArray = message.content.split(" ");
            let args = messageArray.slice(1);
            const filePath = __dirname + "/comptes/" + args[0] + ".txt";
            fs.writeFile(filePath, 'GalackQSM:GalackQSM', function (err) {
                if (err) throw err;
                const embed = {
                    title: "Service created!",
                    description: "Service created successfully `" + args[0] + "`!",
                    color: 0xff033d,
                    timestamp: new Date(),
                    author: {
                        name: botname + " - account generator",
                        url: "https://discord.gg/DekcZ9xMud",
                        icon_url: bot.displayAvatarURL
                    },
                    fields: []
                };
                message.channel.send({ embed });
            });
        }
        if (command === "restock") {
            const embed = {
                title: "Thank you for putting a service!",
                description: "Please provide the name of the replenished service!",
                color: 0xff033d,
                timestamp: new Date(),
                author: {
                    name: botname + " - account generator ",
                    url: "https://discord.gg/DekcZ9xMud",
                    icon_url: bot.displayAvatarURL
                },
                fields: []
            };
            let messageArray = message.content.split(" ");
            let args = messageArray.slice(1);
            if (!message.member.hasPermission("ADMINISTRATOR"))
                return message.reply("You don't have the permissions to do this!");
            if (!args[0])
            {
                return message.channel.send({ embed });
            }
            if (!args[1])
            {
                return message.channel.send({ embed });
            }
            else {
            message.channel.send("@everyone\n● Account restock: **" + args[0] + "**\n● Number of restock accounts: **" + args[1] + " Accounts(s)**\n● Restock by: " + "<@" + message.author.id +">");
            }
        }
    }
});

bot.login(config.token);
