from app import app, db
import sys

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
