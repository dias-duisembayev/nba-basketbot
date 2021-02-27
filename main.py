import os
from requests import HTTPError

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

import api_calls


TOKEN = os.getenv('NBA_BASKETBOT_TOKEN')
PLAYER_INFO, PLAYER_AVERAGE, PLAYER_RECENT_STAT = range(3)


def start(update, context):
    """Send an introductory message when the command /start is issued."""
    update.message.reply_text('Hello, I am NBA Basketbot! Use command /info to get more info on commands')


def send_info(update, context):
    """Send info on commands that the bot can execute"""
    info = '*Type /player to get some basic info on a particular player.\n' \
           '*Type /average to get current season\'s average stat for a particular player.\n' \
           '*Type /recent to get a list of recently played games and their score (including live games).\n' \
           '*Type /stat to get a player\'s stat in any recent games'
    update.message.reply_text(info)


def refer_to_info(update, context):
    """Sends reminder of /info command"""
    refer_to_info_text = 'Please type /info in order to see the commands'
    update.message.reply_text(refer_to_info_text)


def notify_timeout(update, context):
    """Sends a message when ConversationHandler has reached a timeout"""
    update.message.reply_text('I am tired of waiting. Hurry up next time :)')


def stop_conversation(update, context):
    """Ends ConversationHandler's dialogue"""
    return ConversationHandler.END


def request_player_name(update, context):
    """Requests a player name from a user"""
    update.message.reply_text('Enter a player\'s name:')
    if update.message.text == '/player':
        return PLAYER_INFO
    elif update.message.text == '/average':
        return PLAYER_AVERAGE
    elif update.message.text == '/stat':
        return PLAYER_RECENT_STAT


def send_players_info(update, context):
    """Finds players by their name and sends basic info"""
    player_name = update.message.text
    update.message.reply_text('This might take several seconds...')
    if player_name == 'Beka':
        update.message.reply_text('Бека - 12Д. Верная рука. Позишн - позишнлес.')
        return ConversationHandler.END
    try:
        players = api_calls.get_players(player_name)
        if players:  # if api call returned at least one player
            for player in players:
                update.message.reply_text(f'{player}')
            return ConversationHandler.END
        else:
            update.message.reply_text('No such player was found')
            return ConversationHandler.END
    except HTTPError:
        update.message.reply_text('An error has occurred. Please try again later')
        return ConversationHandler.END


def send_players_average_stat(update, context):
    """Finds players by their name and sends current season's average stats"""
    player_name = update.message.text
    try:
        update.message.reply_text('This might take several seconds...')
        players = api_calls.get_players(player_name)
        if players:  # if api call returned at least one player
            for player in players:
                average_stat = api_calls.get_player_average_stat(player)
                update.message.reply_text(average_stat)
            return ConversationHandler.END
        else:
            update.message.reply_text('No such player was found')
            return ConversationHandler.END
    except HTTPError:
        update.message.reply_text('An error has occurred. Please try again later')
        return ConversationHandler.END


def send_recent_games_info(update, context):
    """Sends info about recent nba games(finished within a day or live games)"""
    try:
        update.message.reply_text('This might take several seconds...')
        games = api_calls.get_recent_games()
        if games:  # if any recent games were found
            for game in games:
                update.message.reply_text(f'{game}')
        else:
            update.message.reply_text('No recent games were found')
    except HTTPError:
        update.message.reply_text('An error has occurred. Please try again later')


def send_player_game_stat(update, context):
    """Sends player's stat in a particular game"""
    player_name = update.message.text
    update.message.reply_text('This takes more than several seconds...')
    try:
        players_stats = api_calls.get_game_stat_for_player(player_name)
        if players_stats:  # if any recent games were found
            for player_stats in players_stats:
                update.message.reply_text(player_stats)
            return ConversationHandler.END
        else:
            update.message.reply_text('No such player/game was found')
            return ConversationHandler.END
    except HTTPError:
        update.message.reply_text('An error has occurred. Please try again later')
        return ConversationHandler.END


def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('info', send_info))
    dp.add_handler(CommandHandler('recent', send_recent_games_info))

    player_info_conv = ConversationHandler(
        entry_points=[CommandHandler('player', request_player_name)],
        states={
            PLAYER_INFO: [
                MessageHandler(Filters.text, send_players_info),
            ],
            ConversationHandler.TIMEOUT: [
                MessageHandler(Filters.text, notify_timeout)
            ]
        },
        fallbacks=[MessageHandler(Filters.text, stop_conversation)],
    )

    player_average_conv = ConversationHandler(
        entry_points=[CommandHandler('average', request_player_name)],
        states={
            PLAYER_AVERAGE: [
                MessageHandler(Filters.text, send_players_average_stat),
            ],
            ConversationHandler.TIMEOUT: [
                MessageHandler(Filters.text, notify_timeout)
            ]
        },
        fallbacks=[MessageHandler(Filters.text, stop_conversation)],
    )
    player_game_stat_conv = ConversationHandler(
        entry_points=[CommandHandler('stat', request_player_name)],
        states={
            PLAYER_RECENT_STAT: [
                MessageHandler(Filters.text, send_player_game_stat),
            ],
            ConversationHandler.TIMEOUT: [
                MessageHandler(Filters.text, notify_timeout)
            ]
        },
        fallbacks=[MessageHandler(Filters.text, stop_conversation)],
    )

    dp.add_handler(player_info_conv)
    dp.add_handler(player_average_conv)
    dp.add_handler(player_game_stat_conv)

    # if user's input is not recognized
    dp.add_handler(MessageHandler(Filters.text, refer_to_info))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
