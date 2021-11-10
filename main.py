from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from coin_scrapper import Scrapper
from threading import Thread

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)
scrapper = Scrapper()

class Paragraph(db.Model):
	__tablename__ = 'Paragraph'
	id = db.Column('id', db.Integer, primary_key=True)
	title = db.Column('title', db.Text, nullable=False)
	source = db.Column('source', db.Text, nullable=False)
	published_time = db.Column('published_time', db.Text, nullable=False)
	cryptocurrency = db.Column('cryptocurrency', db.Text, nullable=False)
	url = db.Column('url', db.Text, nullable=False)

	def __init__(self, **fields):
		self.title = fields['title']
		self.source = fields['source']
		self.published_time = fields['published_time']
		self.cryptocurrency = fields['cryptocurrency']
		self.url = fields['url']


@app.route("/coin", methods=['GET'])
def coin():
	coin = request.args.get('coin')
	if not coin:
		return render_template("index.html")
	else:
		thread = Thread(target=scrapper.get_news_of_cryptocurrency, args=(coin,))
		thread.start()

		while thread.is_alive():
			continue

		for paragraph in scrapper.last_result:
			paragraph = Paragraph(**paragraph)
			db.session.add(paragraph)
			db.session.commit()

		context = {"paragraphs": scrapper.last_result, "input_text": coin}
		return render_template("index.html", **context)

@app.route("/shutdown")
def shutdown():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	return "Good bye"

if __name__ == "__main__": # if the code starts in the console
	app.run(debug=True)
