from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Ensure index.html extends base.html as well.

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/services/ai')
def servicesai():
    return render_template('ai.html')

@app.route('/services/software')
def servicessoftware():
    return render_template('software.html')

@app.route('/services/sodium')
def servicessodium():
    return render_template('sodium.html')

@app.route('/services/webs')
def serviceswebs():
    return render_template('webs.html')

@app.route('/services/projects')
def servicesprojects():
    return render_template('projects.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False in production
# Note: Ensure you have the necessary HTML files in a 'templates' directory.