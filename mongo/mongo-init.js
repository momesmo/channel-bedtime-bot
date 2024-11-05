db = db.getSiblingDB('discord_bot');

// Create a new user for the discord_bot database
db.createUser({
    user: 'user',
    pwd: 'password',
    roles: [
        {
            role: 'readWrite',
            db: 'discord_bot'
        }
    ]
});

// Create some initial collections
db.createCollection('guilds');
db.createCollection('users');
db.createCollection('guild_settings');


// Create indexes
db.guilds.createIndex({ "guild_id": 1 }, { unique: true });
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.guild_settings.createIndex({ "guild_id": 1 }, { unique: true });