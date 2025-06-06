from flask import Flask, render_template, request, redirect, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DIFFICULTY_LEVELS = {
    'easy': (1, 50, 2),
    'medium': (1, 100, 3),
    'hard': (1, 200, 5)
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        level = request.form['difficulty']
        min_val, max_val, max_attempts = DIFFICULTY_LEVELS[level]
        secret_number = random.randint(min_val, max_val)

        session['secret_number'] = secret_number
        session['attempts_left'] = max_attempts
        session['difficulty'] = level
        session['range'] = f"{min_val} to {max_val}"
        session['score'] = 0
        session['message'] = ""

        return redirect('/game')

    return render_template('index.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'secret_number' not in session:
        return redirect('/')

    message = session.get('message', '')
    if request.method == 'POST':
        try:
            guess = int(request.form['guess'])
        except ValueError:
            session['message'] = "Enter a valid number!"
            return redirect('/game')

        secret_number = session['secret_number']
        attempts_left = session['attempts_left']

        if guess == secret_number:
            session['score'] += 1
            message = f"🎉 Correct! The number was {secret_number}. Score: {session['score']}"
            # Reset with new number
            min_val, max_val, _ = DIFFICULTY_LEVELS[session['difficulty']]
            session['secret_number'] = random.randint(min_val, max_val)
            session['attempts_left'] = DIFFICULTY_LEVELS[session['difficulty']][2]
        else:
            session['attempts_left'] -= 1
            if session['attempts_left'] == 0:
                message = f"💥 Game Over! The number was {secret_number}. Your score: {session['score']}"
                session.clear()
                return render_template('game.html', message=message, game_over=True)

            if guess < secret_number:
                message = f"🔻 Too low! Attempts left: {session['attempts_left']}"
            else:
                message = f"🔺 Too high! Attempts left: {session['attempts_left']}"

        session['message'] = message
        return redirect('/game')

    return render_template('game.html', message=message, range=session['range'],
                           score=session['score'], attempts=session['attempts_left'], game_over=False)

if __name__ == '__main__':
    app.run(debug=True)
