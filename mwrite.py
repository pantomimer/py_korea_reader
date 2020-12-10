# 必要モジュールをインポートする
import sqlite3


# print("終了します")
# exit()

# データベースに接続する
conn = sqlite3.connect('yoja.db')
c = conn.cursor()

# テーブルの作成
#c.execute('''CREATE TABLE users(id real, name text, birtyday text)''')

# データの挿入

with open('yoja.txt', "r") as file:
	for text in file:
		text = text.replace( '\n' , '' ).strip()
		if text != "" :
			# print(text)
			c.execute("INSERT INTO sentences (sentence) VALUES ('" + text + "')")
#c.execute("INSERT INTO users VALUES (2, '学習 次郎', '2006-05-05')")
#c.execute("INSERT INTO users VALUES (3, '牌存 花子', '2017-09-10')")

# 挿入した結果を保存（コミット）する
conn.commit()

# データベースへのアクセスが終わったら close する
conn.close()
