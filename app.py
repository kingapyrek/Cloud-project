from py2neo import Graph
from flask import Flask
from flask import render_template
from flask import url_for
from flask import flash
from flask import redirect
from flask import request


uri = "neo4j+s://580b1b03.databases.neo4j.io:7687"
user = "neo4j"
password = "K-Z2uM60c91BTR4lZvD1Q29wu44UozYXc4gAyghmDQs"

graph = Graph(uri, auth = (user, password))

app=Flask(__name__)
app.secret_key = 'super secret key'
app.static_folder = 'static'

@app.route("/")
@app.route("/home")
def route_home():
    return(render_template('index.html'))

@app.route("/add_person")
def route_add():
    women = list_women()
    man = list_man()
    all = list_all()
    return(render_template('add_person.html', women = women, man = man, all = all))



@app.route("/find_person")
def route_find_person():
    return(render_template('find_person_form.html', all = list_all()))

@app.route("/find_path")
def route_find_path():
    return(render_template('find_path_form.html', all = list_all()))

@app.route("/find/path", methods=['GET', 'POST'])
def show_path():
    if request.method == "POST":
        if request.form["submit"] == "find_path":
            name1 = request.form['name1']
            name2 = request.form['name2']
            path = find_path(name1, name2)
            if (path):
                path = str(path[0]['path'])

                replacement = ["(", ")", "{", "}", ":"]
                for r in replacement:
                    path = path.replace(r, "")
    return(render_template('show_path.html', path = path))

@app.route("/show_all")
def route_show_all():
    people = list_all_people()
    print(people)
    return(render_template('show_all.html', people = people))

@app.route("/find/person", methods=['GET', 'POST'])
def find_person_info():
     if request.method == "POST":
        if request.form["submit"] == "find_person":
            name = request.form['name']
            person = get_person(name)
            mother = get_mother(name)
            father = get_father(name)
            siblings = get_siblings(name)
            married = get_marriages(name)
            divorced = get_divorces(name)
            grandparents = get_grandparents(name)
            cousins = get_cousins(name)
            children = get_children(name)
            grandchildren = get_grandchildren(name)
            print(cousins)
            return(render_template('show_person_info.html', name = name, person = person, mother = mother, father = father, 
            siblings= siblings, married = married, divorced = divorced, grandparents = grandparents, cousins = cousins, children = children, grandchildren = grandchildren))
            

@app.route("/add/person", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        if request.form["submit"] == "add_person":
            print(request.form)
            properties_string = ""
            person = {}
            for key, value in request.form.items():
                if value != "" and key != "submit":
                    if key in ["name", "birth", "died", "gender"]:
                        properties_string += key + ": '" + value + "', "
                    
                    person[key] = value
            properties_string = properties_string[:-2]
            query = "CREATE (:Person {" + properties_string + "})"
            graph.run(query)
            
    
            if 'mother' in person.keys():
                query_mother =  f"MATCH (k:Person), (m:Person) " + \
                f"WHERE k.name = '" + person['name'] + f"' AND m.name ='" + person['mother'] + \
                f"' CREATE (k)-[r:MOTHER]->(m) RETURN type(r)"
                graph.run(query_mother)
            
            if 'father' in person.keys():
                query_father = f"MATCH (k:Person), (f:Person) " + \
                f"WHERE k.name = '" + person['name'] + f"' AND f.name ='" + person['father'] + \
                f"' CREATE (k)-[r:FATHER]->(f) RETURN type(r)"
                graph.run(query_father)

            if 'divorced' in person.keys() and 'spouse' in person.keys():
                query_divorce = f"MATCH (p1:Person), (p2:Person)" +\
                    f"WHERE p1.name = '" + person['name'] + f"'AND p2.name='" + person['spouse'] + \
                    "' CREATE (p1)-[r:DIVORCED { married:  '" + str(person['married_since']) + "', divorced: '" + str(person['divorced']) +"'} ]->(p2) RETURN type(r)"
                graph.run(query_divorce)
            
            if 'spouse' in person.keys() and 'divorced' not in person.keys():
                query_spouse = f"MATCH (p1:Person), (p2:Person)" +\
                    f"WHERE p1.name = '" + person['name'] + f"'AND p2.name='" + person['spouse'] + \
                    "' CREATE (p1)-[r:MARRIED {since:  '" + str(person['married_since']) + "'} ]->(p2) RETURN type(r)"
                graph.run(query_spouse)

            flash('Add new person: ' + person['name'], 'success')
            return redirect(url_for('route_add'))
    else:
        return redirect(url_for('route_add'))


def find_path(name1, name2):
    query = "MATCH (p1:Person {name: '" + name1 + "'}), (p2:Person {name: '" + name2 + "'})," + \
            "path = shortestPath((p1)-[*]-(p2)) RETURN path"
    result = graph.run(query).data()
    return result      

def list_women():
    query = "Match(p:Person) where p.gender = 'f' RETURN p.name as name"
    result = graph.run(query).data()
    return result

def list_man():
    query = "Match(p:Person) where p.gender = 'm' RETURN p.name as name"
    result = graph.run(query).data()
    return result

def list_all():
    query = "Match(p:Person) RETURN p.name as name"
    result = graph.run(query).data()
    return result

def list_all_people():
    query = "Match(p:Person) RETURN p"
    result = graph.run(query).data()
    return result

def get_person(name):
    query = "MATCH (p:Person) " + \
            "WHERE p.name = '" + name + "'" + \
            "RETURN p"
    result = graph.run(query).data()
    return result

def get_mother(name):
    query = "MATCH (:Person {name: '" + name + "'})-[mr:MOTHER]->(m) " + \
            "RETURN m, mr"
    result = graph.run(query).data()
    return result

def get_father(name):
    query = "MATCH (:Person {name: '" + name + "'})-[fr:FATHER]->(f) " + \
            "RETURN f, fr"
    result = graph.run(query).data()
    return result

def get_marriages(name):
    query = "Match(p:Person{name: '" + name + "'})" + \
            "MATCH ((p)-[r:MARRIED]-(s))" + \
            "RETURN s, type(r), r.since"
    result = graph.run(query).data()
    return result

def get_divorces(name):
    query = "Match(p:Person{name: '" + name + "'})" + \
            "MATCH ((p)-[r:DIVORCED]-(s))" + \
            "RETURN s, type(r), r.married, r.divorced"
    result = graph.run(query).data()
    return result

def get_siblings(name):
    query = "MATCH(p:Person), (parent:Person), (sib:Person)" + \
         "WHERE (p.name='" + name + "' AND  ((p)-[:MOTHER]->(parent) AND (sib)-[:MOTHER]->(parent)) AND (p.name <> sib.name))" + \
         "OR (p.name='" + name + "' AND (p)-[:FATHER]->(parent) AND (sib)-[:FATHER]->(parent)" + \
         "AND (p.name <> sib.name)) RETURN DISTINCT sib"
    result = graph.run(query).data()
    return result

def get_grandparents(name):
    query = "Match(k:Person {name: '" + name + "'}), (p:Person), (g:Person)" + \
    "WHERE (((k)-[:MOTHER]->(p) AND (p)-[:MOTHER]->(g))" + \
    "OR ((k)-[:MOTHER]->(p) AND (p)-[:FATHER]->(g))" + \
    "OR ((k)-[:FATHER]->(p) AND (p)-[:MOTHER]->(g))" + \
    "OR ((k)-[:FATHER]->(p) AND (p)-[:FATHER]->(g)))" + \
    "RETURN g"
    result = graph.run(query).data()
    return result

def get_cousins(name):
    query = "Match(k:Person {name:'" + name + "'}), (p:Person), (g:Person), (c:Person), (cousin:Person)" + \
            "WHERE ((k)-[:MOTHER]->(p)-[:MOTHER]->(g)<-[:MOTHER]-(c)<-[:FATHER]-(cousin))" + \
            "OR ((k)-[:MOTHER]->(p)-[:MOTHER]->(g)<-[:MOTHER]-(c)<-[:MOTHER]-(cousin))" + \
            "OR ((k)-[:MOTHER]->(p)-[:FATHER]->(g)<-[:FATHER]-(c)<-[:FATHER]-(cousin))" + \
            "OR ((k)-[:MOTHER]->(p)-[:FATHER]->(g)<-[:FATHER]-(c)<-[:MOTHER]-(cousin))" + \
            "OR ((k)-[:FATHER]->(p)-[:MOTHER]->(g)<-[:MOTHER]-(c)<-[:FATHER]-(cousin))" + \
            "OR ((k)-[:FATHER]->(p)-[:MOTHER]->(g)<-[:MOTHER]-(c)<-[:MOTHER]-(cousin))" + \
            "OR ((k)-[:FATHER]->(p)-[:FATHER]->(g)<-[:FATHER]-(c)<-[:FATHER]-(cousin))" + \
            "OR ((k)-[:FATHER]->(p)-[:FATHER]->(g)<-[:FATHER]-(c)<-[:MOTHER]-(cousin))" + \
            "RETURN DISTINCT cousin"
    result = graph.run(query).data()
    return result

def get_children(name):
    query = "MATCH (p:Person {name:'" + name + "'}), (c:Person)" +\
            "WHERE ((p)<-[:MOTHER]-(c))" + \
            "OR ((p)<-[:FATHER]-(c))" +\
            "RETURN c"
    result = graph.run(query).data()
    return result

def get_grandchildren(name):
    query = "MATCH (p:Person {name:'" + name + "'}), (c:Person), (g:Person)" + \
            "WHERE ((p)<-[:FATHER]-(c)<-[:FATHER]-(g))" + \
            "OR ((p)<-[:FATHER]-(c)<-[:MOTHER]-(g))" + \
            "OR ((p)<-[:MOTHER]-(c)<-[:FATHER]-(g))" + \
            "OR ((p)<-[:MOTHER]-(c)<-[:MOTHER]-(g))" + \
            "RETURN g"
    result = graph.run(query).data()
    return result

if __name__ == '__main__':
    app.run(port=5050)
