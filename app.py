import os
import time
import json
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

app = Flask(__name__)   # create our flask app
app.secret_key = os.environ.get('SECRET_KEY')


# configure Twitter API
instaConfig = {
	'client_id':os.environ.get('CLIENT_ID'),
	'client_secret':os.environ.get('CLIENT_SECRET'),
	'redirect_uri' : os.environ.get('REDIRECT_URI')
}
api = InstagramAPI(**instaConfig)

@app.route('/')

def user_photos():
	# ser = serial.Serial('COM3', 9600)
	# inByte = ser.read()	
	
	# if instagram info is in session variables, then display user photos
	if 'instagram_access_token' in session and 'instagram_user' in session:
		userAPI = InstagramAPI(access_token=session['instagram_access_token'])

		geomedia, next = userAPI.tag_recent_media(tag_name = 'wild')

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : geomedia,
			'serial' : inByte
		}
		return render_template('display5.html', **templateData)
			
	else:
		return redirect('/connect')
	
# Redirect users to Instagram for login
@app.route('/connect')
def main():

	url = api.get_authorize_url(scope=["likes","comments"])
	return redirect(url)

# Instagram will redirect users back to this route after successfully logging in
@app.route('/instagram_callback')
def instagram_callback():

	code = request.args.get('code')

	if code:

		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'

		app.logger.debug('got an access token')
		app.logger.debug(access_token)

		# Sessions are used to keep this data 
		session['instagram_access_token'] = access_token
		session['instagram_user'] = user

		return redirect('/') # redirect back to main page
		
	else:
		return "Uhoh no code provided"


	
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# This is a jinja custom filter
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    pyDate = time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y') # convert twitter date string into python date/time
    return time.strftime('%Y-%m-%d %h:%M:%S', pyDate) # return the formatted date.
    
# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)