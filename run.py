from flask import Flask, render_template, send_file, url_for, request, escape
from random import randrange
import subprocess, smtplib, json

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/input-error")
def inputError():
    return render_template('input-error.html')

@app.route("/results", methods = ['POST'])
def results():
    websiteURL = request.form['website']

    # make sure the input is only one word
    if len(websiteURL) == 0:
        message = "The URL is not provided. Please provide an input."
        return render_template('home.html', message=message)
    elif len(websiteURL.split()) > 1:
        message = "More than one input is provided: \"" + websiteURL + "\". Please provide only one URL input."
        return render_template('home.html', message=message)

    # if copied_websites is greater than a gigabyte, remove copied_websites and everything in it and recreate it to save storage
    output = subprocess.check_output(["du", "-hcs", "copied_websites/"])
    outputList = output.decode("utf-8").split()
    if outputList[0].endswith('G'):
        subprocess.check_output(["rm", "-rf", "copied_websites"])
        subprocess.check_output(["mkdir", "copied_websites"])
    
    # if user did not specify http or https, use https
    if not websiteURL.startswith('http://') and not websiteURL.startswith('https://'):
        websiteURL = 'https://' + websiteURL

    # make name of website file using a very random number.
    # this is necessary because website file name cannot be the URL if the URL contains any '/'
    # and using a counter shows numbers of websites copied so far
    websiteFilename = str(randrange(1000000000, 9999999999))

    # copy the website, save the website folder, and zip the website folder
    try:
        subprocess.check_output(["httrack", websiteURL, "-O", "copied_websites/" + websiteFilename])
    except:
        return render_template('errors/502.html')
    subprocess.check_output(["zip", "-r", "copied_websites/" + websiteFilename + ".zip", "copied_websites/" + websiteFilename])

    # get ZIP file's size
    output = subprocess.check_output(["du", "-h", "copied_websites/" + websiteFilename + ".zip"])
    outputList = output.decode("utf-8").split()
    if outputList[0].endswith('K'):
        outputList[0] = outputList[0].replace('K', ' Kilobyte(s)')
    elif outputList[0].endswith('M'):
        outputList[0] = outputList[0].replace('M', ' Megabytes(s)')
    elif outputList[0].endswith('G'):
        outputList[0] = outputList[0].replace('G', ' Gigabytes(s)')
    else:
        output[0] = "less than a kilobyte"
    
    header = "Copying \"" + websiteURL + "\" Completed!"
    return render_template('results.html', header=header, size=outputList[0], websiteFilename=websiteFilename)

@app.route('/copied_websites/<websiteFilename>.zip')
def copiedWebsite(websiteFilename):
    return send_file('copied_websites/' + escape(websiteFilename) + '.zip')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/contacting", methods = ['POST'])
def contacting():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    fullMessage = "\r\nName: " + name + "\r\nEmail: " + email + "\r\nSubject: " + subject + "\r\nMessage:\r\n" + message

    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(config['EMAIL_USER'], config['EMAIL_PASS'])
    s.sendmail(config['EMAIL_USER'], config['EMAIL_USER'], fullMessage)	
    s.quit()
    #config.close()

    return render_template('contact.html', success=True)

@app.route("/privacy")
@app.route("/privacy-policy")
def privacyPolicy():
    return render_template('privacy-policy.html')

@app.errorhandler(404)
def error404(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def error403(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(502)
def error502(error):
    return render_template('errors/502.html'), 502

@app.errorhandler(500)
@app.errorhandler(Exception)
def error500(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
