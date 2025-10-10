from app import create_app
from models import db, User, Tip
from werkzeug.security import generate_password_hash


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # create default nurse if missing
        nurse = User.query.filter_by(username='nurse').first()
        if not nurse:
            nurse = User(username='nurse', password=generate_password_hash('password'), role='nurse')
            db.session.add(nurse)
            print('Added nurse user (username: nurse, password: password)')
        else:
            print('Nurse user already exists')

        # sample tips
        samples = [
            dict(title='Early prenatal visits', content='Visit your clinic early in pregnancy for check-ups and tests.', language='en', audio_filename='example_en.mp3'),
            dict(title='Nutrition during pregnancy', content='Eat balanced meals and take recommended supplements.', language='en', audio_filename=None),
        ]

        for s in samples:
            exists = Tip.query.filter_by(title=s['title']).first()
            if not exists:
                t = Tip(title=s['title'], content=s['content'], language=s['language'], audio_filename=s['audio_filename'])
                db.session.add(t)
                print(f"Added tip: {s['title']}")
            else:
                print(f"Tip already present: {s['title']}")

        db.session.commit()


if __name__ == '__main__':
    seed()
