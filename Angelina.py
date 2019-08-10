#!/home/quinn/Applications/bin/python
import discord
import random
import subprocess
import sys
import re
import datetime
import json

CHANNEL_TYPE_TEXT = discord.channel.TextChannel
DIRECT_MESSAGE = discord.channel.DMChannel

with open('/etc/angelina.conf', 'r') as config_file:
  config_string = config_file.read()
CONFIG = json.loads(config_string)

OWNER_ID = int(CONFIG['owner_id'])
MY_MENTION_PREFIX = CONFIG['my_mention_prefix']

reflections = {
    "am": "are",
    "was": "were",
    "i": "you",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "are": "am",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you"
}

psychobabble = [
    [r'I need (.*)',
     ["Why do you need {0}?",
      "Would it really help you to get {0}?",
      "Are you sure you need {0}?"]],

    [r'Why don\'?t you ([^\?]*)\??',
     ["Do you really think I don't {0}?",
      "Perhaps eventually I will {0}.",
      "Do you really want me to {0}?"]],

    [r'Why can\'?t I ([^\?]*)\??',
     ["Do you think you should be able to {0}?",
      "If you could {0}, what would you do?",
      "I don't know -- why can't you {0}?",
      "Have you really tried?"]],

    [r'I can\'?t (.*)',
     ["How do you know you can't {0}?",
      "Perhaps you could {0} if you tried.",
      "What would it take for you to {0}?"]],

    [r'I am (.*)',
     ["Did you come to me because you are {0}?",
      "How long have you been {0}?",
      "How do you feel about being {0}?"]],

    [r'I\'?m (.*)',
     ["How does being {0} make you feel?",
      "Do you enjoy being {0}?",
      "Why do you tell me you're {0}?",
      "Why do you think you're {0}?"]],

    [r'Are you ([^\?]*)\??',
     ["Why does it matter whether I am {0}?",
      "Would you prefer it if I were not {0}?",
      "Perhaps you believe I am {0}.",
      "I may be {0} -- what do you think?"]],

    [r'What (.*)',
     ["Why do you ask?",
      "How would an answer to that help you?",
      "What do you think?"]],

    [r'How (.*)',
     ["How do you suppose?",
      "Perhaps you can answer your own question.",
      "What is it you're really asking?"]],

    [r'Because (.*)',
     ["Is that the real reason?",
      "What other reasons come to mind?",
      "Does that reason apply to anything else?",
      "If {0}, what else must be true?"]],

    [r'(.*) sorry (.*)',
     ["There are many times when no apology is needed.",
      "What feelings do you have when you apologize?"]],

    [r'Hello(.*)',
     ["Hello... I'm glad you could drop by today.",
      "Hi there... how are you today?",
      "Hello, how are you feeling today?"]],

    [r'I think (.*)',
     ["Do you doubt {0}?",
      "Do you really think so?",
      "But you're not sure {0}?"]],

    [r'(.*) friend (.*)',
     ["Tell me more about your friends.",
      "When you think of a friend, what comes to mind?",
      "Why don't you tell me about a childhood friend?"]],

    [r'Yes',
     ["You seem quite sure.",
      "OK, but can you elaborate a bit?"]],

    [r'(.*) computer(.*)',
     ["Are you really talking about me?",
      "Does it seem strange to talk to a computer?",
      "How do computers make you feel?",
      "Do you feel threatened by computers?"]],

    [r'Is it (.*)',
     ["Do you think it is {0}?",
      "Perhaps it's {0} -- what do you think?",
      "If it were {0}, what would you do?",
      "It could well be that {0}."]],

    [r'It is (.*)',
     ["You seem very certain.",
      "If I told you that it probably isn't {0}, what would you feel?"]],

    [r'Can you ([^\?]*)\??',
     ["What makes you think I can't {0}?",
      "If I could {0}, then what?",
      "Why do you ask if I can {0}?"]],

    [r'Can I ([^\?]*)\??',
     ["Perhaps you don't want to {0}.",
      "Do you want to be able to {0}?",
      "If you could {0}, would you?"]],

    [r'You are (.*)',
     ["Why do you think I am {0}?",
      "Does it please you to think that I'm {0}?",
      "Perhaps you would like me to be {0}.",
      "Perhaps you're really talking about yourself?"]],

    [r'You\'?re (.*)',
     ["Why do you say I am {0}?",
      "Why do you think I am {0}?",
      "Are we talking about you, or me?"]],

    [r'I don\'?t (.*)',
     ["Don't you really {0}?",
      "Why don't you {0}?",
      "Do you want to {0}?"]],

    [r'I feel (.*)',
     ["Good, tell me more about these feelings.",
      "Do you often feel {0}?",
      "When do you usually feel {0}?",
      "When you feel {0}, what do you do?"]],

    [r'I have (.*)',
     ["Why do you tell me that you've {0}?",
      "Have you really {0}?",
      "Now that you have {0}, what will you do next?"]],

    [r'I would (.*)',
     ["Could you explain why you would {0}?",
      "Why would you {0}?",
      "Who else knows that you would {0}?"]],

    [r'Is there (.*)',
     ["Do you think there is {0}?",
      "It's likely that there is {0}.",
      "Would you like there to be {0}?"]],

    [r'My (.*)',
     ["I see, your {0}.",
      "Why do you say that your {0}?",
      "When your {0}, how do you feel?"]],

    [r'You (.*)',
     ["We should be discussing you, not me.",
      "Why do you say that about me?",
      "Why do you care whether I {0}?"]],

    [r'Why (.*)',
     ["Why don't you tell me the reason why {0}?",
      "Why do you think {0}?"]],

    [r'I want (.*)',
     ["What would it mean to you if you got {0}?",
      "Why do you want {0}?",
      "What would you do if you got {0}?",
      "If you got {0}, then what would you do?"]],

    [r'(.*) mother(.*)',
     ["Tell me more about your mother.",
      "What was your relationship with your mother like?",
      "How do you feel about your mother?",
      "How does this relate to your feelings today?",
      "Good family relations are important."]],

    [r'(.*) father(.*)',
     ["Tell me more about your father.",
      "How did your father make you feel?",
      "How do you feel about your father?",
      "Does your relationship with your father relate to your feelings today?",
      "Do you have trouble showing affection with your family?"]],

    [r'(.*) child(.*)',
     ["Did you have close friends as a child?",
      "What is your favorite childhood memory?",
      "Do you remember any dreams or nightmares from childhood?",
      "Did the other children sometimes tease you?",
      "How do you think your childhood experiences relate to your feelings today?"]],

    [r'(.*)\?',
     ["Why do you ask that?",
      "Please consider whether you can answer your own question.",
      "Perhaps the answer lies within yourself?",
      "Why don't you tell me?"]],

    [r'quit',
     ["Thank you for talking with me.",
      "Good-bye.",
      "Thank you, that will be $150.  Have a good day!"]],

    [r'(.*)',
     ["Please tell me more.",
      "Let's change focus a bit... Tell me about your family.",
      "Can you elaborate on that?",
      "Why do you say that {0}?",
      "I see.",
      "Very interesting.",
      "{0}.",
      "I see.  And what does that tell you?",
      "How does that make you feel?",
      "How do you feel when you say that?"]]
]

def logprint(m):
  f = open("Angelina.log", "a")
  f.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
  f.write(" ")
  f.write(str(m))
  f.write("\n")
  f.close()

def reflect(fragment):
    tokens = fragment.lower().split()
    for i, token in enumerate(tokens):
        if token in reflections:
            tokens[i] = reflections[token]
    return ' '.join(tokens)


def analyze(statement):
    for pattern, responses in psychobabble:
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
            response = random.choice(responses)
            return response.format(*[reflect(g) for g in match.groups()])

class MyClient(discord.Client):
  owner_user = None
  async def send_stats(self,dco):
    user_dict = {}
    total_messages = 0
    total_channels = 0
    destination_channel = None
    guild = dco.guild
    valid_members = []
    for member in guild.members:
      add_member_id = member.id
      valid_members.append(add_member_id)
    for channel in guild.channels:
      if isinstance(channel,CHANNEL_TYPE_TEXT):
        if (channel.id==dco.id):
          destination_channel = channel
        total_channels += 1
        messages = await channel.history(limit=1000).flatten()
        for message in messages:
          who_said = message.author.name
          total_messages += 1
          not_including_this_user = (message.author.bot or message.author.id==456226577798135808)
          if not message.author.id in valid_members:
            not_including_this_user = True
          if not not_including_this_user:
            if who_said=='Deleted User' and message.author.discriminator=='0000':
              print(message.author.id)
            who_said_final = who_said + '#' + message.author.discriminator
            if not who_said_final in user_dict:
              user_dict[who_said_final] = 1
            else:
              user_dict[who_said_final] += 1
    total_messages = str(total_messages)
    total_channels = str(total_channels)
    stats_message = "I have looked at a total of " + total_messages + " messages over " + total_channels + " total text channels, limiting myself to the most recent 1000 messages in each channel, the top 40 users and their message counts in my dataset follow:\n\n```"
    # sort user_dict based on the values rather than the keys, returns an
    # ordered list of the keys which we can then iterate to get the values
    # in sorted order from lowest to highest
    user_list = sorted(user_dict, key=user_dict.__getitem__, reverse=True)
    i = 0
    for user in user_list:
      if (i < 40):
        i += 1
        stats_message = stats_message + str(i) + ". " + user + " with " + str(user_dict[user]) + " messages\n"
    stats_message = stats_message + "```"
    await destination_channel.send(stats_message)
  async def on_ready(self):
    sent_welcome_message = False
    for member in self.get_all_members():
      if member.id==OWNER_ID:
        self.owner_user = member
        if not sent_welcome_message:
          sent_welcome_message = True
          welcome_messages = [
            "Pumped up and ready to rock! ❤",
            "Hey there!  I'm all gussied up and online now! ❤",
            "Your gassy dragon is ready for playtime again!  :joy_cat:"
            ]
          welcome_message = random.choice(welcome_messages)
          await self.owner_user.send(welcome_message)
  def is_command(self, message):
    if isinstance(message.channel,DIRECT_MESSAGE):
      return (message.content.startswith('!') or message.content.startswith('.') or message.content.startswith('#'))
    return (message.content.startswith(self.user.name+"."))
  def get_command(self, message):
    if isinstance(message.channel,DIRECT_MESSAGE):
      return message.content[1:]
    return message.content.split('.',1)[1]
  def can_run_command(self, message, allow_others=True):
    if (message.author.id==OWNER_ID):
      return True
    if allow_others:
      for role in message.author.roles:
        if (role.name=="Admin"):
          return True
    return False
  def get_channel(self, guild, channel_id):
    for channel_found in guild.channels:
      if channel_found.id == channel_id:
        return channel_found
    raise RuntimeError("No channel found with the specified ID in the given guild, this should never happen!")
    sys.exit(1)
  async def send_channel_only_error(self, message):
    await message.channel.send("Sorry!  I can't do that in direct messages!  Help a squishy dragon out and ask me in a text channel?")
  async def on_member_join(self, member):
    ##
    ## This isn't great, but for now, all this stuff is special case handling
    ##
    if member.guild.id==587137611982700546:
      channel_to = self.get_channel(message.guild, 590043331719987200)
      enrollment_channel = self.get_channel(message.guild, 588037825941864456).mention
      roles_channel = self.get_channel(message.guild, 587918735201927174).mention
      await channel_to.send("Hello, "+member.mention+"!  Please scroll to the top of the "+enrollment_channel+" and accept the rules to start chatting, you can also acquire roles in the "+roles_channel+".  We hope you enjoy your time here!")
  async def on_message(self, message):
    if message.author == self.user:
      # Stop playing with yourself!!!
      return
    #
    # Logging
    #
    if isinstance(message.channel, DIRECT_MESSAGE):
      logprint("Direct message from "+message.author.name+": "+str(message.content))
      #pass
    if isinstance(message.channel, CHANNEL_TYPE_TEXT):
      logprint("Channel message from "+message.author.name+" in "+message.guild.name+": "+message.content)
      #pass
    # 
    # Special case command processing
    # 

    #
    # General command processing
    #
    if message.content == 'ping':
      await message.channel.send('pong')
      return
    if (isinstance(message.channel,CHANNEL_TYPE_TEXT) or isinstance(message.channel,DIRECT_MESSAGE)):
      if not (self.is_command(message) and self.can_run_command(message)):
        if message.content.startswith(MY_MENTION_PREFIX):
        # the above might need an "and" re-added with the message.channel dual-type check from about 5 lines previous
          if not isinstance(message.channel,DIRECT_MESSAGE):
            chat_msg = message.content.split(" ",1)[1].strip()
            await message.channel.send("<@"+str(message.author.id)+"> "+analyze(chat_msg))
          else:
            chat_msg = message.content
            await message.channel.send(analyze(chat_msg))
      else:
        command = self.get_command(message)
        if command=="stats":
          if isinstance(message.channel,CHANNEL_TYPE_TEXT):
            await message.channel.send("I'll start gathering statistics now, this process usually takes a few minutes...")
            await self.send_stats(message.channel)
          else:
            await self.send_channel_only_error(message)
        elif command=="channel_only_test":
          await self.send_channel_only_error(message)
        elif command=="status":
          v = "```"+subprocess.run(['uptime'], stdout=subprocess.PIPE).stdout.decode('utf-8')+"```"
          w = "```"+subprocess.run(['uname','-a'], stdout=subprocess.PIPE).stdout.decode('utf-8')+"```"
          x = "```"+subprocess.run(['free','-mt'], stdout=subprocess.PIPE).stdout.decode('utf-8')+"```"
          y = "```"+subprocess.run(['df','-h'], stdout=subprocess.PIPE).stdout.decode('utf-8')+"```"
          z = "```"+subprocess.run(['cat','/proc/cpuinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')+"```"
          await message.channel.send("I've got you covered! ❤\n"+v+w+x+y+z)
        elif command=="shutdown" or command=="reload" or command=="reboot" or command=="restart":
          if self.can_run_command(message,allow_others=False):
            await message.channel.send("I'll be back momentarily!")
            sys.exit(0)
        elif command=="info":
          await message.channel.send("I've got nothing, sorry!")
        elif command=="system" or command=="whoareyou" or command=="whoareu" or command=="whoru":
          x = subprocess.run(['hostname'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
          y = subprocess.run(['uname','-a'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
          if command=="whoareyou" or command=="whoareu" or command=="whoru":
            await message.channel.send("♫ Whoo who?  Whoo who? ♫ ❤")
          await message.channel.send("I am {}: {}".format(x,y))
        elif command.startswith("shell ") or command.startswith("run "):
          if self.can_run_command(message,allow_others=False):
            command = command.split(" ",1)[1]
            await message.channel.send("Working on it!")
            await message.channel.send("```"+subprocess.run(command.split(" "), stdout=subprocess.PIPE).stdout.decode('utf-8')[:1920].strip()+"```")
            await message.channel.send("All done!")
          else:
            await message.channel.send("<@"+str(message.author.id)+">, you're not the boss of me!  ")
        else:
          await message.channel.send("<@"+str(message.author.id)+">, you jerk!  I don't know what you want me to do!")
      return
logprint("I'm coming up for service!")
client = MyClient()
client.run(CONFIG['bot_token'])
