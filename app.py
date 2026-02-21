import html
import os
import sqlite3
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "running_club.db")
DB_PATH = os.environ.get("RUNNING_CLUB_DB_PATH", DEFAULT_DB_PATH)
STATIC_DIR = os.path.join(BASE_DIR, "static")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                birth_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS races (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                race_date TEXT NOT NULL,
                distance_km REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, city, race_date)
            );

            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                runner_id INTEGER NOT NULL,
                race_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(runner_id, race_id),
                FOREIGN KEY(runner_id) REFERENCES runners(id),
                FOREIGN KEY(race_id) REFERENCES races(id)
            );
            """
        )


def parse_post_data(environ):
    try:
        size = int(environ.get("CONTENT_LENGTH", "0"))
    except ValueError:
        size = 0
    body = environ["wsgi.input"].read(size).decode("utf-8")
    parsed = parse_qs(body)
    return {k: v[0].strip() for k, v in parsed.items()}


def redirect(start_response, location):
    start_response("303 See Other", [("Location", location)])
    return [b""]


def page_layout(title, active_nav, content, flash=""):
    nav_items = [
        ("/", "Accueil"),
        ("/coureurs", "Coureurs"),
        ("/courses", "Courses"),
        ("/inscriptions", "Inscriptions"),
        ("/synthese", "Synthèse"),
    ]
    nav_html = "".join(
        f'<a class="nav-link {"active" if path == active_nav else ""}" href="{path}">{label}</a>'
        for path, label in nav_items
    )
    flash_html = f'<p class="flash">{html.escape(flash)}</p>' if flash else ""

    return f"""<!doctype html>
<html lang=\"fr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)} - Club Running</title>
  <link rel=\"stylesheet\" href=\"/static/style.css\" />
</head>
<body>
  <header class=\"topbar\">
    <h1>Club Running</h1>
    <p>Site de gestion des inscriptions aux courses</p>
    <nav>{nav_html}</nav>
  </header>
  <main>
    {flash_html}
    {content}
  </main>
</body>
</html>"""


def rows_or_empty(rows, formatter, colspan=4):
    if not rows:
        return f'<tr><td colspan="{colspan}">Aucune donnée pour le moment.</td></tr>'
    return "".join(formatter(row) for row in rows)


def query_flash(environ):
    return parse_qs(environ.get("QUERY_STRING", "")).get("message", [""])[0]


def home(environ, start_response):
    content = """
<section class="card">
  <h2>Bienvenue</h2>
  <p>Ce site permet à votre club de running de:</p>
  <ul>
    <li>Créer des profils coureurs,</li>
    <li>Ajouter des courses,</li>
    <li>Inscrire les coureurs aux courses existantes,</li>
    <li>Consulter une vue synthétique des participations.</li>
  </ul>
  <p>Utilisez le menu pour naviguer.</p>
</section>
"""
    page = page_layout("Accueil", "/", content, flash=query_flash(environ))
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [page.encode("utf-8")]


def runners_page(environ, start_response):
    with get_connection() as conn:
        runners = conn.execute(
            "SELECT id, first_name, last_name, email, birth_date FROM runners ORDER BY last_name, first_name"
        ).fetchall()

    content = f"""
<section class="card">
  <h2>Nouveau coureur</h2>
  <form method="post" action="/runners">
    <label>Prénom<input required name="first_name" /></label>
    <label>Nom<input required name="last_name" /></label>
    <label>Email<input required type="email" name="email" /></label>
    <label>Date de naissance<input required type="date" name="birth_date" /></label>
    <button type="submit">Créer le compte</button>
  </form>
</section>
<section class="card">
  <h2>Liste des coureurs</h2>
  <table>
    <thead><tr><th>Prénom</th><th>Nom</th><th>Email</th><th>Date de naissance</th></tr></thead>
    <tbody>
      {rows_or_empty(runners, lambda row: f'<tr><td>{html.escape(row["first_name"])}</td><td>{html.escape(row["last_name"])}</td><td>{html.escape(row["email"])}</td><td>{html.escape(row["birth_date"])}</td></tr>')}
    </tbody>
  </table>
</section>
"""
    page = page_layout("Coureurs", "/coureurs", content, flash=query_flash(environ))
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [page.encode("utf-8")]


def races_page(environ, start_response):
    with get_connection() as conn:
        races = conn.execute(
            "SELECT name, city, race_date, distance_km FROM races ORDER BY race_date, name"
        ).fetchall()

    content = f"""
<section class="card">
  <h2>Ajouter une course</h2>
  <form method="post" action="/races">
    <label>Nom de la course<input required name="name" /></label>
    <label>Ville<input required name="city" /></label>
    <label>Date<input required type="date" name="race_date" /></label>
    <label>Distance (km)<input required type="number" step="0.1" min="0.1" name="distance_km" /></label>
    <button type="submit">Ajouter la course</button>
  </form>
</section>
<section class="card">
  <h2>Courses disponibles</h2>
  <table>
    <thead><tr><th>Nom</th><th>Ville</th><th>Date</th><th>Distance</th></tr></thead>
    <tbody>
      {rows_or_empty(races, lambda row: f'<tr><td>{html.escape(row["name"])}</td><td>{html.escape(row["city"])}</td><td>{html.escape(row["race_date"])}</td><td>{row["distance_km"]} km</td></tr>')}
    </tbody>
  </table>
</section>
"""
    page = page_layout("Courses", "/courses", content, flash=query_flash(environ))
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [page.encode("utf-8")]


def registrations_page(environ, start_response):
    with get_connection() as conn:
        runners = conn.execute(
            "SELECT id, first_name, last_name FROM runners ORDER BY last_name, first_name"
        ).fetchall()
        races = conn.execute(
            "SELECT id, name, city, race_date FROM races ORDER BY race_date, name"
        ).fetchall()
        registrations = conn.execute(
            """
            SELECT r.first_name, r.last_name, rc.name, rc.city, rc.race_date
            FROM registrations reg
            JOIN runners r ON reg.runner_id = r.id
            JOIN races rc ON reg.race_id = rc.id
            ORDER BY rc.race_date, r.last_name
            """
        ).fetchall()

    runner_options = "".join(
        f'<option value="{r["id"]}">{html.escape(r["first_name"])} {html.escape(r["last_name"])}</option>'
        for r in runners
    )
    race_options = "".join(
        f'<option value="{rc["id"]}">{html.escape(rc["name"])} ({html.escape(rc["city"])} - {html.escape(rc["race_date"])})</option>'
        for rc in races
    )

    content = f"""
<section class="card">
  <h2>Inscrire un coureur</h2>
  <form method="post" action="/registrations">
    <label>Coureur
      <select required name="runner_id">
        <option value="">-- Sélectionner --</option>
        {runner_options}
      </select>
    </label>
    <label>Course
      <select required name="race_id">
        <option value="">-- Sélectionner --</option>
        {race_options}
      </select>
    </label>
    <button type="submit">Enregistrer l'inscription</button>
  </form>
</section>
<section class="card">
  <h2>Inscriptions en cours</h2>
  <table>
    <thead><tr><th>Coureur</th><th>Course</th><th>Ville</th><th>Date</th></tr></thead>
    <tbody>
      {rows_or_empty(registrations, lambda row: f'<tr><td>{html.escape(row["first_name"])} {html.escape(row["last_name"])}</td><td>{html.escape(row["name"])}</td><td>{html.escape(row["city"])}</td><td>{html.escape(row["race_date"])}</td></tr>')}
    </tbody>
  </table>
</section>
"""
    page = page_layout("Inscriptions", "/inscriptions", content, flash=query_flash(environ))
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [page.encode("utf-8")]


def summary_page(environ, start_response):
    with get_connection() as conn:
        by_runner = conn.execute(
            """
            SELECT r.first_name, r.last_name, COUNT(reg.id) AS race_count
            FROM runners r
            LEFT JOIN registrations reg ON reg.runner_id = r.id
            GROUP BY r.id
            ORDER BY r.last_name, r.first_name
            """
        ).fetchall()
        by_race = conn.execute(
            """
            SELECT rc.name, rc.city, rc.race_date, COUNT(reg.id) AS participant_count
            FROM races rc
            LEFT JOIN registrations reg ON reg.race_id = rc.id
            GROUP BY rc.id
            ORDER BY rc.race_date, rc.name
            """
        ).fetchall()

    content = f"""
<div class="grid">
  <section class="card">
    <h2>Synthèse par coureur</h2>
    <table>
      <thead><tr><th>Coureur</th><th>Nombre de courses</th></tr></thead>
      <tbody>
        {rows_or_empty(by_runner, lambda row: f'<tr><td>{html.escape(row["first_name"])} {html.escape(row["last_name"])}</td><td>{row["race_count"]}</td></tr>', colspan=2)}
      </tbody>
    </table>
  </section>
  <section class="card">
    <h2>Synthèse par course</h2>
    <table>
      <thead><tr><th>Course</th><th>Date</th><th>Participants</th></tr></thead>
      <tbody>
        {rows_or_empty(by_race, lambda row: f'<tr><td>{html.escape(row["name"])} ({html.escape(row["city"])})</td><td>{html.escape(row["race_date"])}</td><td>{row["participant_count"]}</td></tr>', colspan=3)}
      </tbody>
    </table>
  </section>
</div>
"""
    page = page_layout("Synthèse", "/synthese", content, flash=query_flash(environ))
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [page.encode("utf-8")]


def create_runner(environ, start_response):
    data = parse_post_data(environ)
    if any(not data.get(k) for k in ["first_name", "last_name", "email", "birth_date"]):
        return redirect(start_response, "/coureurs?message=Tous%20les%20champs%20sont%20obligatoires")

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO runners(first_name, last_name, email, birth_date) VALUES (?, ?, ?, ?)",
                (data["first_name"], data["last_name"], data["email"], data["birth_date"]),
            )
    except sqlite3.IntegrityError:
        return redirect(start_response, "/coureurs?message=Email%20deja%20utilise")

    return redirect(start_response, "/coureurs?message=Coureur%20cree")


def create_race(environ, start_response):
    data = parse_post_data(environ)
    if any(not data.get(k) for k in ["name", "city", "race_date", "distance_km"]):
        return redirect(start_response, "/courses?message=Tous%20les%20champs%20sont%20obligatoires")

    try:
        distance = float(data["distance_km"])
        if distance <= 0:
            raise ValueError
    except ValueError:
        return redirect(start_response, "/courses?message=Distance%20invalide")

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO races(name, city, race_date, distance_km) VALUES (?, ?, ?, ?)",
                (data["name"], data["city"], data["race_date"], distance),
            )
    except sqlite3.IntegrityError:
        return redirect(start_response, "/courses?message=Cette%20course%20existe%20deja")

    return redirect(start_response, "/courses?message=Course%20ajoutee")


def create_registration(environ, start_response):
    data = parse_post_data(environ)
    if not data.get("runner_id") or not data.get("race_id"):
        return redirect(start_response, "/inscriptions?message=Selectionnez%20un%20coureur%20et%20une%20course")

    try:
        runner_id = int(data["runner_id"])
        race_id = int(data["race_id"])
    except ValueError:
        return redirect(start_response, "/inscriptions?message=Identifiants%20invalides")

    try:
        with get_connection() as conn:
            runner_exists = conn.execute("SELECT 1 FROM runners WHERE id = ?", (runner_id,)).fetchone()
            race_exists = conn.execute("SELECT 1 FROM races WHERE id = ?", (race_id,)).fetchone()
            if not runner_exists or not race_exists:
                return redirect(start_response, "/inscriptions?message=Coureur%20ou%20course%20introuvable")

            conn.execute(
                "INSERT INTO registrations(runner_id, race_id) VALUES (?, ?)",
                (runner_id, race_id),
            )
    except sqlite3.IntegrityError:
        return redirect(start_response, "/inscriptions?message=Inscription%20deja%20existante")

    return redirect(start_response, "/inscriptions?message=Inscription%20enregistree")


def static_asset(environ, start_response):
    path = environ.get("PATH_INFO", "")
    if path != "/static/style.css":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    css_path = os.path.join(STATIC_DIR, "style.css")
    try:
        with open(css_path, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    start_response("200 OK", [("Content-Type", "text/css; charset=utf-8")])
    return [content]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path.startswith("/static/") and method == "GET":
        return static_asset(environ, start_response)

    if path == "/" and method == "GET":
        return home(environ, start_response)
    if path == "/coureurs" and method == "GET":
        return runners_page(environ, start_response)
    if path == "/courses" and method == "GET":
        return races_page(environ, start_response)
    if path == "/inscriptions" and method == "GET":
        return registrations_page(environ, start_response)
    if path == "/synthese" and method == "GET":
        return summary_page(environ, start_response)

    if path == "/runners" and method == "POST":
        return create_runner(environ, start_response)
    if path == "/races" and method == "POST":
        return create_race(environ, start_response)
    if path == "/registrations" and method == "POST":
        return create_registration(environ, start_response)

    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Not Found"]


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    with make_server("0.0.0.0", port, application) as server:
        print(f"Site disponible sur http://localhost:{port}")
        server.serve_forever()
