from StudyApp import app

if __name__ == '__main__':
    app.run(debug=True)

"""
    from StudyApp import db, app
    app.app_context().push()
    db.create_all()
"""