import re
from urllib import request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from py2neo import Graph, Node, Relationship

global_var = {}

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

#host is Neo4j AuraDB link for online social graph hosting
graph = Graph(scheme="neo4j",secure=True, host="DB_URI", port= PORT_NUMBER, auth=('DB-USER', 'DB-PASSWORD'))


def get_userid(username: str):
    
    query = """
    MATCH (n:name {name: $username})
    RETURN n.id AS id
    """
    result = graph.run(query, username=username)

    # Process the query result
    user_id = result.evaluate()

    return user_id


def handle_message(update: Update, context):
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username
    
    print(f"User ID: {user_id}, Username: {username}")


def start(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    user_id = update.effective_user.id

    user_node = Node("Persons", name=username, id=user_id)
    graph.merge(user_node, "name", "id")

    start_message = '''You have joined the social graph! 
    
    type "/request @username" to send a request to be connected to someone else who has joined the social graph
    Note: this is CaSe SenSItIvE!
    
    type "/graph" to see your mutual connections in your own social graph
    '''

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=start_message,
    )

    print("start: completed")


def neo4jRelationMaker(sender_name,sender_id,receiver_name,receiver_id,message):
    sender = graph.nodes.match("Persons", name=sender_name, id=sender_id).first()
    receiver = graph.nodes.match("Persons", name=receiver_name, id=receiver_id).first()
    print("neo4jRelationMaker: received request")
    
    if sender and receiver:
        relationship = Relationship(sender, message, receiver)
        graph.create(relationship)


def request(update: Update, context: CallbackContext) -> None:
    sender_name = update.effective_user.username
    sender_id = update.effective_user.id
    receiver_name = re.findall(r'@(\w+)', update.message.text)[0]
    receiver_id = get_userid(receiver_name)

    neo4jRelationMaker(sender_name,sender_id,receiver_name,receiver_id,"SENT")
    print ("neo4jRelationMaker: sent request")
    
    keyboard = [
        [InlineKeyboardButton("Accept", callback_data="accept"),
         InlineKeyboardButton("Decline", callback_data="decline")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard to the specified user ID
    variable_string = "{}".format(sender_name) + " sent a request to connect!"

    # Store the sender name in context with the name of the reciever id and request
    global_var[f"{receiver_id}"]=sender_name
  
    context.bot.send_message(
        chat_id=receiver_id,
        text=variable_string,
        reply_markup=reply_markup
    )

def graphDraw(update: Update, context: CallbackContext) -> None:
    sender_name = update.effective_user.username

    print("graph started")

    keyboard = [
        # change url to a localhost or host through a github url
        [InlineKeyboardButton("Link", url="URL_LINK" + "?s=" + sender_name)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard to the specified user ID
    variable_string = "Click the link below for your own social graph!"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=variable_string,
        reply_markup=reply_markup
    )

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == "accept":

       neo4jRelationMaker(
        update.effective_user.username,
        update.effective_user.id,
        global_var[f"{update.effective_user.id}"],
        get_userid(global_var[f"{update.effective_user.id}"]),        
        "RECEIVED"
       )
       query.edit_message_text(text="You accepted the request.")

    elif query.data == "decline":
        query.edit_message_text(text="You declined the request.")


start_handler = CommandHandler('start', start)
request_handler = CommandHandler('request', request)
graphDraw_handler = CommandHandler('graph', graphDraw)
message_handler = MessageHandler(Filters.text, handle_message)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(request_handler)
dispatcher.add_handler(graphDraw_handler)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_callback))
dispatcher.add_handler(message_handler)

updater.start_polling()