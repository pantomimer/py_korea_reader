# 必要モジュールをインポートする
import sqlite3
import MeCab
import subprocess
from subprocess import PIPE
from translate import Translator
from colorama import Fore, Back, Style
translator= Translator(from_lang="ko",to_lang="ja")
m = MeCab.Tagger()

def to_ja(text):
	if ' ' in text:
		proc = subprocess.run('trans -no-ansi -b {ko=ja} "' + text + '"', shell=True, stdout=PIPE, stderr=PIPE, text=True)
		res = proc.stdout.splitlines()
		return res[0]
	else:
		proc = subprocess.run('trans -no-ansi -show-original n -show-original-phonetics n -show-translation-phonetics n -show-prompt-message n -show-languages n -show-languages n -show-original-dictionary n -show-dictionary n -show-translation n -indent 0 {ko=ja} "' + text + '"', shell=True, stdout=PIPE, stderr=PIPE, text=True)
		res = proc.stdout.splitlines()
		return res[1]


# データベースに接続する
conn = sqlite3.connect('yoja.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 最初はis_read=0の最初
c.execute('SELECT * FROM sentences where(is_read = 0) ORDER BY id ASC limit 1')
row = c.fetchone()
sentence_id = row['id']

# 大ループ
while True:
	sql = 'SELECT * FROM sentences where(id = ' + str(sentence_id) + ')'
	# print(sql)
	c.execute(sql)
	row = c.fetchone()
	# レコードを取得する
	if row is None:
		exit("end")
	is_read = row['is_read']
	print('[' + str(sentence_id) + ']')
	print(row['sentence'])
	print("------------")
	word = [row['sentence']]
	# translation = translator.translate(row['sentence'])
	# print(translation)
	mlist = m.parse(row['sentence']).splitlines()
	for index, item in enumerate(mlist):
		if item != "EOS":
			# print("[" + str(index) + "]" + " " + item)
			surface = item.split("\t")[0]
			word.append(surface)
	# print (word)


	#プロンプトのループ
	for index, item in enumerate(word):
		forecolor = Fore.WHITE
		c.execute('SELECT * FROM words where(word = "' + item + '")')
		row = c.fetchone()
		if row is None:
			forecolor = Fore.WHITE
		else:
			if row["check_num"] >= 1:
				forecolor = Fore.RED
			else:
				forecolor = Fore.BLUE
		if index == 0:
			print(forecolor + "[" + str(index) + "]" + " " + item)
		else:
			print(forecolor + "[" + str(index) + "]" + " " + item, end='  ')
	while True:
		print(Fore.WHITE)
		val = input("? : ")
		if val.isdecimal():
			numval = int(val)
			check_word = word[numval]
			print (check_word)
			# wordsにあるかチェック
			c.execute('SELECT * FROM words where(word = "' + check_word + '")')
			row = c.fetchone()
			if row is None:
				# print('no data')
				translation = to_ja(check_word)
				# print (Fore.WHITE + "初めてです")
				print(Fore.WHITE + "[a] " + translation)
				sql = "INSERT INTO words (word, mean, read_num, check_num) VALUES ('" + check_word + "', '" + translation + "', 0, 1);"
				# print (sql)
				c.execute(sql)
				conn.commit()
			else:
				if row['mean'] is None:
					translation = to_ja(check_word)
					print ( Fore.WHITE + "[a] " + translation , end=' ')
					print ( Fore.WHITE + "(" + str(row['check_num'] + 1) + ")")
					sql = "UPDATE words SET check_num = check_num + 1, mean = '" + translation + "' Where(word = '" + check_word + "')"
				else:
					print ( Fore.WHITE + "[a] " + row['mean'] , end=' ')
					print ( Fore.WHITE + "(" + str(row['check_num'] + 1) + ")")
					sql = "UPDATE words SET check_num = check_num + 1 Where(word = '" + check_word + "')"

				# print (sql)
				c.execute(sql)
				conn.commit()
		# 直前の単語を変更
		if val == 'a':
			new_word = input(check_word + "に意味を追加します : ")
			c.execute('SELECT * FROM words where(word = "' + check_word + '")')
			row = c.fetchone()
			sql = "UPDATE words SET mean = '" + row['mean'] + ", " + new_word + "' Where(word = '" + check_word + "')"
			print (sql)
			c.execute(sql)
			conn.commit()

		# リピート
		if val == 'r' or val == '':
			break

		# 終了
		if val == 'q':
			exit("Bye")
		# 次へ
		if val == 'n':
			if is_read == 0:
				# すべて記録して次に行く
				# wordsにあるかチェック
				for item in word:
					c.execute('SELECT * FROM words where(word = "' + item + '")')
					row = c.fetchone()
					if row is None:
						sql = "INSERT INTO words (word, read_num, check_num) VALUES ('" + item + "', 1, 0);"
						# print (Fore.WHITE + sql)
						c.execute(sql)
						conn.commit()
					else:
						sql = "UPDATE words SET read_num = read_num + 1 Where(word = '" + item + "')"
						# print (Fore.WHITE + sql)
						c.execute(sql)
						conn.commit()
				sql = "UPDATE sentences SET is_read = 1 Where(id = " + str(sentence_id) + ")"
				# print (Fore.WHITE + sql)
				c.execute(sql)
				conn.commit()
			#Endif
			sentence_id += 1
			break
		# ひとつ前に戻る
		if val == 'b':
			sentence_id -= 1
			break
		# 最後に読んだところまで戻る
		if val == 'c':
			c.execute('SELECT * FROM sentences where(is_read = 0) ORDER BY id ASC limit 1')
			row = c.fetchone()
			sentence_id = row['id']
			break

	# Endwhile プロンプト
# Endwhile 大ループ


# データベースへのアクセスが終わったら close する
conn.close()
