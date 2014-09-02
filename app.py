import math
import random
import string

from flask import Flask, abort, send_from_directory, session, redirect, render_template, request, url_for
from flask_peewee.db import Database
from peewee import *

from werkzeug.contrib.fixers import ProxyFix

DATABASE = {
    'name': 'babynames.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'QV3KBDOFMK1NYDOPYT5WL7F8TNB12345T'

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
db = Database(app)


class Knowledge(db.Model):
    name = CharField(unique=True)
    meaning = TextField()
    pronounce = CharField()
    gender = CharField()
    origin = CharField()


class Seen(db.Model):
    frm = ForeignKeyField(Knowledge, related_name='frm')
    to = ForeignKeyField(Knowledge, related_name='to')
    count = IntegerField(default=1)


class Wiki(db.Model):
    name = CharField()
    first_name = CharField()
    last_name = CharField()
    alternative_names = CharField()
    birth_date = CharField()
    birth_place = CharField()
    death_date = CharField()
    death_place = CharField()
    short_desc = CharField()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=['POST'])
def search():
    q = request.form['q']
    if q and isinstance(q, (str, unicode)):
        return redirect(url_for("knowledge", name=q))
    else:
        return redirect(url_for("index"))


@app.route("/name/<name>", methods=['GET'])
def knowledge(name):
    try:
        name = Knowledge.get(name=name)
        seen_id = session.get('seen', None)

        if seen_id and seen_id != name.id:
            try:
                seen = int(seen_id)
                seen = Knowledge.get(id=seen)
                frm = Seen.get(frm=seen, to=name)
                frm.count += 1
                frm.save()
            except DoesNotExist:
                Seen.create(frm=seen, to=name)

        try:
            seen = Seen.select().where(
                Seen.to == name.id
            ).order_by(Seen.count.desc()).limit(20)
        except DoesNotExist:
            seen = None
            pass

        try:
            famous = Wiki.select().where(
                Wiki.name ** ("%" + name.name + "%")
            ).order_by(fn.Random()).limit(50)
        except DoesNotExist:
            famous = None
            pass

        session['seen'] = name.id

    except DoesNotExist:
        return redirect(url_for("index"))
    return render_template("knowledge.html", item=name, seen=seen, famous=famous)


@app.route("/chars")
@app.route("/chars/<char>")
@app.route("/chars/<char>/<int:page>")
def chars(char=None, page=1):
    if char:
        char = char.lower()[0]
        items = Knowledge.select(Knowledge.name).where(
            fn.Lower(fn.Substr(Knowledge.name, 1, 1)) == char
        ).order_by(Knowledge.name)
        return object_list("char.html", items, 'item', paginate_by=42, page=page, item=items, char=char.upper())
    else:
        return render_template("chars.html", item=sort_by_column(string.ascii_uppercase))


@app.route("/genders")
@app.route("/genders/<gender>")
@app.route("/genders/<gender>/<int:page>")
def genders(gender="", page=1):
    gender = gender.lower()
    if gender in ["boy", "girl", "unisex"]:
        items = Knowledge.select(Knowledge.name).where(
            Knowledge.gender == gender[0]
        ).order_by(Knowledge.name)
        return object_list("gender.html", items, 'item', paginate_by=42, page=page, item=items, gender=gender)
    else:
        return render_template("genders.html")


@app.route("/origins")
@app.route("/origins/<origin>")
@app.route("/origins/<origin>/<int:page>")
def origins(origin="", page=1):
    origin_list = [u'african american',
                   u'african american (modern)',
                   u'african american (rare)',
                   u'afrikaans',
                   u'akan',
                   u'albanian',
                   u'algonquin',
                   u'american (hispanic)',
                   u'amharic',
                   u'ancient aramaic',
                   u'ancient celtic',
                   u'ancient celtic (latinized)',
                   u'ancient egyptian',
                   u'ancient egyptian (hellenized)',
                   u'ancient germanic',
                   u'ancient germanic (latinized)',
                   u'ancient greek',
                   u'ancient greek (anglicized)',
                   u'ancient greek (latinized)',
                   u'ancient irish',
                   u'ancient near eastern',
                   u'ancient near eastern (anglicized)',
                   u'ancient near eastern (hellenized)',
                   u'ancient near eastern (latinized)',
                   u'ancient persian',
                   u'ancient persian (hellenized)',
                   u'ancient roman',
                   u'ancient roman (anglicized)',
                   u'ancient roman (rare)',
                   u'ancient scandinavian',
                   u'anglo-saxon',
                   u'anglo-saxon (latinized)',
                   u'anglo-saxon mythology',
                   u'apache',
                   u'arabic',
                   u'arabic (anglicized)',
                   u'arabic (latinized)',
                   u'armenian',
                   u'armenian mythology',
                   u'arthurian romance',
                   u'astronomy',
                   u'aymara',
                   u'azerbaijani',
                   u'aztec and toltec mythology',
                   u'baltic mythology',
                   u'bashkir',
                   u'basque',
                   u'belarusian',
                   u'bengali',
                   u'berber',
                   u'biblical',
                   u'biblical greek',
                   u'biblical hebrew',
                   u'biblical latin',
                   u'bosnian',
                   u'breton',
                   u'bulgarian',
                   u'bulgarian (archaic)',
                   u'catalan',
                   u'caucasian mythology',
                   u'celtic mythology',
                   u'celtic mythology (latinized)',
                   u'chechen',
                   u'chinese',
                   u'choctaw',
                   u'circassian',
                   u'comanche',
                   u'coptic',
                   u'cornish',
                   u'corsican',
                   u'cree',
                   u'croatian',
                   u'croatian (rare)',
                   u'czech',
                   u'czech (archaic)',
                   u'dagestani',
                   u'danish',
                   u'danish (rare)',
                   u'dutch',
                   u'dutch (archaic)',
                   u'dutch (rare)',
                   u'eastern african',
                   u'egyptian mythology',
                   u'egyptian mythology (anglicized)',
                   u'egyptian mythology (hellenized)',
                   u'egyptian mythology (latinized)',
                   u'english',
                   u'english (archaic)',
                   u'english (australian)',
                   u'english (british',
                   u'english (british)',
                   u'english (modern)',
                   u'english (new zealand)',
                   u'english (rare)',
                   u'esperanto',
                   u'estonian',
                   u'estonian (rare)',
                   u'ewe',
                   u'far eastern mythology',
                   u'finnish',
                   u'finnish (rare)',
                   u'finnish mythology',
                   u'french',
                   u'french (archaic)',
                   u'french (rare)',
                   u'frisian',
                   u'galician',
                   u'ganda',
                   u'georgian',
                   u'georgian (archaic)',
                   u'georgian (rare)',
                   u'georgian mythology',
                   u'german',
                   u'german (archaic)',
                   u'german (rare)',
                   u'german (swiss)',
                   u'germanic mythology',
                   u'greek',
                   u'greek mythology',
                   u'greek mythology (anglicized)',
                   u'greek mythology (latinized)',
                   u'greenlandic',
                   u'hawaiian',
                   u'hebrew',
                   u'hinduism',
                   u'history',
                   u'hungarian',
                   u'hungarian (rare)',
                   u'ibibio',
                   u'icelandic',
                   u'igbo',
                   u'incan mythology',
                   u'indian',
                   u'indian (sikh)',
                   u'indigenous australian',
                   u'indonesian',
                   u'ingush',
                   u'inuit',
                   u'iranian',
                   u'iranian (rare)',
                   u'irish',
                   u'irish (latinized)',
                   u'irish (rare)',
                   u'irish mythology',
                   u'iroquois',
                   u'italian',
                   u'italian (archaic)',
                   u'italian (modern)',
                   u'italian (rare)',
                   u'japanese',
                   u'jewish',
                   u'judeo-christian legend',
                   u'kazakh',
                   u'khmer',
                   u'kikuyu',
                   u'korean',
                   u'kurdish',
                   u'kyrgyz',
                   u'late greek',
                   u'late greek (latinized)',
                   u'late roman',
                   u'latvian',
                   u'limburgish',
                   u'literature',
                   u'lithuanian',
                   u'low german',
                   u'low german (archaic)',
                   u'luhya',
                   u'luo',
                   u'macedonian',
                   u'manx',
                   u'maori',
                   u'mapuche',
                   u'mayan',
                   u'mayan mythology',
                   u'medieval czech',
                   u'medieval czech (latinized)',
                   u'medieval english',
                   u'medieval english (latinized)',
                   u'medieval french',
                   u'medieval german',
                   u'medieval italian',
                   u'medieval mongolian',
                   u'medieval occitan',
                   u'medieval scandinavian',
                   u'medieval slavic',
                   u'medieval spanish',
                   u'medieval turkic',
                   u'modern',
                   u'mongolian',
                   u'mormon',
                   u'mwera',
                   u'mythology',
                   u'nahuatl',
                   u'native american',
                   u'navajo',
                   u'ndebele',
                   u'near eastern mythology',
                   u'near eastern mythology (hellenized)',
                   u'near eastern mythology (latinized)',
                   u'new world mythology',
                   u'norse mythology',
                   u'northern african',
                   u'norwegian',
                   u'norwegian (rare)',
                   u'nuu-chah-nulth',
                   u'occitan',
                   u'ojibwe',
                   u'old church slavic',
                   u'old danish',
                   u'old norman',
                   u'ossetian',
                   u'ottoman turkish',
                   u'pacific/polynesian',
                   u'pacific/polynesian mythology',
                   u'pakistani',
                   u'pashto',
                   u'persian mythology',
                   u'persian mythology (hellenized)',
                   u'pet',
                   u'polish',
                   u'polish (archaic)',
                   u'polish (rare)',
                   u'popular culture',
                   u'portuguese',
                   u'portuguese (brazilian)',
                   u'portuguese (rare)',
                   u'punjabi',
                   u'quechua',
                   u'rare',
                   u'roman mythology',
                   u'roman mythology (anglicized)',
                   u'romanian',
                   u'russian',
                   u'russian (archaic)',
                   u'russian (rare)',
                   u'sami',
                   u'scandinavian (rare)',
                   u'scottish',
                   u'scottish (rare)',
                   u'serbian',
                   u'shawnee',
                   u'shona',
                   u'sioux',
                   u'slavic mythology',
                   u'slovak',
                   u'slovene',
                   u'sotho',
                   u'southern african',
                   u'spanish',
                   u'spanish (archaic)',
                   u'spanish (latin american)',
                   u'spanish (rare)',
                   u'swahili',
                   u'swedish',
                   u'swedish (archaic)',
                   u'swedish (rare)',
                   u'tagalog',
                   u'tajik',
                   u'tamil',
                   u'tatar',
                   u'thai',
                   u'theology',
                   u'tibetan',
                   u'tswana',
                   u'tumbuka',
                   u'turkish',
                   u'turkmen',
                   u'ukrainian',
                   u'ukrainian (rare)',
                   u'urdu',
                   u'urdu (rare)',
                   u'uyghur',
                   u'uzbek',
                   u'various',
                   u'vietnamese',
                   u'welsh',
                   u'welsh (archaic)',
                   u'welsh (rare)',
                   u'welsh mythology',
                   u'western african',
                   u'xhosa',
                   u'yao',
                   u'yiddish',
                   u'yoruba',
                   u'zapotec',
                   u'zulu']

    origin = origin.lower()
    if origin in origin_list:
        items = Knowledge.select(Knowledge.name).where(
            Knowledge.origin % ("*%s*" % origin)
        ).order_by(Knowledge.name)

        print items
        return object_list("origin.html", items, 'item', paginate_by=42, page=page, item=items, origin=origin)
    else:
        return render_template("origins.html", origins=sort_by_column(origin_list))


@app.route("/names")
def names(page=1):
    items = Knowledge.select(Knowledge.name).order_by(Knowledge.name)
    return object_list("names.html", items, 'item', paginate_by=42, page=page, item=items, char='')


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            #abort(403)
            return None


def sort_by_column(list=[], column=3):
    c = column
    list = sorted(list)
    r = int(math.ceil(len(list) / c)) + (1 if len(list) % c is not 0 else 0)

    index = 0
    table1 = []
    for x in range(c):
        table1.append([])
        for y in range(r):
            if len(list) > index:
                table1[x].append(y)
                table1[x][y] = list[index]
                index += 1

    items = []
    for i in range(r):
        for x in table1:
            try:
                items.append(x[i])
            except IndexError:
                items.append("")
                pass

    return items


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    return session['_csrf_token']


def object_list(template_name, qr, var_name='object_list', **kwargs):
    """
    Object list method override for manual page value declaration
    """
    kwargs.update(
        page=int(request.args.get('page', kwargs.get('page', 1))),
        pages=qr.count() / kwargs.get('paginate_by', 20) + 1
    )
    kwargs[var_name] = qr.paginate(kwargs['page'], kwargs.get('paginate_by', 20))
    return render_template(template_name, **kwargs)


if __name__ == "__main__":
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    app.run(
        #host="0.0.0.0",
        #port=int("8080"),
        debug=True)
