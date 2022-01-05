# Команда /history
# После ввода команды пользователю выводится история поиска отелей. Сама история
# содержит:
# 1. Команду, которую вводил пользователь.
# 2. Дату и время ввода команды.
# 3. Отели, которые были найдены.
def history_func(bot, user_message, sql):
    sql.execute("""SELECT * FROM commands""")
    rows = sql.fetchall()
    for row in rows:
        bot.send_message(user_message.chat.id, 'Команда: ' + str(row[0]) +
                         '\nДата и время вызова: ' + str(row[1]) +
                         '\nОтели: ' + str(row[2]))
