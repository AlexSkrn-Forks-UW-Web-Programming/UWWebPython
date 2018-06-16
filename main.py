"""Contains routes and views(?) to handle templates (.jinja2 files)."""

import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session

from model import SavedTotal

app = Flask(__name__)
# app.secret_key = b'\xb6x(\xd67\x1f\xa7\x15\x92\xf1VqU\xe9|\xbcqu\xac\xf6\x16\xa8\x8f\xe5'
app.secret_key = os.environ.get('SECRET_KEY').encode()

# @app.route('/')
# def home():
#     return redirect(url_for('add'))
#
@app.route('/retrieve')
def retrieve():
    # Retrieve code argument from the user's code sumbission
    # Compare to request.form method because retrieve form uses GET method
    code = request.args.get('code', None)

    # If the user is visiting the retrieve page (did not submit form yet):
        # Then just render the retrieve.jinja2 template
    # But if they did submit the form:
        # Then attempt to retrieve the SavedTotal that has the provided code
        # Then save the total from that SavedTotal into session["total"]
        # Then redirect the user back to the main 'add' page

    if code is None:
        return render_template("retrieve.jinja2")
    try:
        saved_total = SavedTotal.get(SavedTotal.code == code)
    except SavedTotal.DoesNotExist:
        return render_template("retrieve.jinja2", error="Code not found")

    session['total'] = saved_total.value

    return redirect(url_for('add'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'total' not in session:
        session['total'] = 0
    if request.method == 'POST':
        # Handle the form submission - which uses POST method
        number = int(request.form['number'])
        session['total'] += number

    return render_template('add.jinja2', session=session)

@app.route('/save', methods=['POST'])
def save():
    total = session.get('total', 0)
    code = base64.b32encode(os.urandom(8)).decode().strip('=')

    saved_total = SavedTotal(value=total, code=code)
    saved_total.save()

    return render_template('save.jinja2', code=code)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    # port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
