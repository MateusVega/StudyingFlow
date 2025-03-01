from StudyApp import app

if __name__ == '__main__':
    app.run(debug=True)

"""
flask db migrate -m "Descrição da mudança"
flask db upgrade

npx @tailwindcss/cli -i ./StudyApp/static/css/input.css -o ./StudyApp/static/css/output.css --minify
"""