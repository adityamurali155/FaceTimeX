from app import app
import sys

if __name__ == '__main__':
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    app.run(host="0.0.0.0", port=8080, debug=True)
