from flask import Blueprint, render_template, session, g, request
from models import Tip

main_bp = Blueprint("main", __name__)

@main_bp.before_app_request
def set_language():
    lang = request.args.get("lang")
    if lang:
        session["lang"] = lang
    g.lang = session.get("lang", "en")

@main_bp.context_processor
def inject_translations():
    translations = {
        "en": {"title": "Health Tips", "book": "Book an Appointment", "read_more": "Read More",
               "welcome": "Welcome to Mobi Mama", "subtitle": "Empowering mothers with healthcare guidance.",
               "login": "Login", "signup": "Sign Up"},
        "tw": {"title": "Apɔw Mu Nkyerɛkyerɛ", "book": "Paw Appɔintment", "read_more": "Kenkan Bio",
               "welcome": "Akwaaba Mobi Mama", "subtitle": "Yɛboa maamefoɔ wɔ Ghana sɛ wɔnya apɔw ho nkyerɛkyerɛ.",
               "login": "Kɔ Mu", "signup": "Bɔ Akawnt"},
    }
    return {"t": translations[g.lang], "current_lang": g.lang}

@main_bp.route("/")
def index():
    lang = g.lang
    tips = Tip.query.filter_by(language=lang).order_by(Tip.created_at.desc()).all()
    return render_template("index.html", tips=tips, lang=lang)

@main_bp.route("/tip/<int:tip_id>")
def tip_detail(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    current_lang = g.lang
    return render_template("tip.html", t=tip, current_lang=current_lang)
