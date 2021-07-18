import datetime

from flask import Blueprint
from flask import render_template, request, redirect, url_for, jsonify
from flask import g

from . import db

bp = Blueprint("pets", "pets", url_prefix="")

def format_date(d):
    if d:
        d = datetime.datetime.strptime(d, '%Y-%m-%d')
        v = d.strftime("%a - %b %d, %Y")
        return v
    else:
        return None

@bp.route("/search/<field>/<value>")
def search(field, value):
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id")
    order = request.args.get("order", "asc")
    print(value)
    arrange = 'p.'+oby
    print(arrange)
    if order == "asc":
        cursor.execute(f'select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s, tags_pets tp, tag t where p.species = s.id and tp.tag = t.id and tp.pet = p.id and t.name = ? order by {arrange}', [value])
    else:
        cursor.execute(f'select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s, tags_pets tp, tag t where p.species = s.id and tp.tag = t.id and tp.pet = p.id and t.name = ? order by {arrange} desc', [value])
    pets = cursor.fetchall()
    return render_template('search.html', field = field, value = value, pets = pets, order="desc" if order=="asc" else "asc")

@bp.route("/")
def dashboard():
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id") # TODO. This is currently not used. 
    order = request.args.get("order", "asc")
    if order == "asc":
        cursor.execute("select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by %s" % ("p."+oby))
    else:
        cursor.execute("select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by %s desc" % ("p."+oby))
    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order="desc" if order=="asc" else "asc")


@bp.route("/<pid>")
def pet_info(pid): 
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
    pet = cursor.fetchone()
    cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
    tags = (x[0] for x in cursor.fetchall())
    name, bought, sold, description, species = pet
    data = dict(id = pid,
                name = name,
                bought = format_date(bought),
                sold = format_date(sold),
                description = description, #TODO Not being displayed
                species = species,
                tags = tags)
    return render_template("petdetail.html", **data)

@bp.route("/<pid>/edit", methods=["GET", "POST"])
def edit(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
        pet = cursor.fetchone()
        print(pet[1])
        cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
        tags = (x[0] for x in cursor.fetchall())
        name, bought, sold, description, species = pet
        data = dict(id = pid,
                    name = name,
                    bought = format_date(bought),
                    sold_raw = sold,
                    sold = format_date(sold),
                    description = description,
                    species = species,
                    tags = tags)
        return render_template("editpet.html", **data)
    elif request.method == "POST":
        description = request.form.get('description')
        sold = request.form.get("sold")
        sold_on=''
        if sold:
            sold_on = request.form.get("sold-on")
        cursor.execute(f"UPDATE PET SET sold = ?, description = ? WHERE id == ?;" , (sold_on,description,pid))
        conn.commit()
        return redirect(url_for("pets.pet_info", pid=pid), 302)
        
    



