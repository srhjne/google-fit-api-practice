from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
import httplib2

from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension

import os
import time
import datetime

app = Flask(__name__)
app.secret_key = "SECRETSECRETSECRET"


@app.route("/")
def homepage():
	return render_template("homepage.html")

@app.route("/steps")
def steps():
	client_id = os.environ["GGL_ID"]
	client_secret = os.environ["GGL_SECRET"]

	scope = "https://www.googleapis.com/auth/fitness.activity.read"
	flow = OAuth2WebServerFlow(client_id, client_secret, scope)

	storage = Storage('credentials.dat')
	credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())

	http = httplib2.Http()
	http = credentials.authorize(http)

	service = build('fitness', 'v1', http=http)


	day =datetime.datetime.now().day
	month = datetime.datetime.now().month
	year = datetime.datetime.now().year
	datestring = ("%0d %0d %0d")%(day,month, year)
	struct_time = time.strptime(datestring, "%d %m %Y")
	millisnow = int(round(time.mktime(struct_time) * 1000))+86400000
	millislast_week = millisnow - 7*86400000

	agg = service.users().dataset().aggregate(userId="me",
		body={"aggregateBy":[{
	    "dataTypeName": "com.google.step_count.delta",
	    "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
	  }],
	  "bucketByTime": { "durationMillis": 86400000 }, # This is 24 hours
	  "startTimeMillis": millislast_week, #start time
	  "endTimeMillis": millisnow # End Time
	  })

	steps_today =  agg.execute()['bucket'][-1]['dataset'][0]['point'][0]['value'][0]['intVal']


	steps_week = []
	for bucket in agg.execute()['bucket']:
		if len(bucket['dataset'][0]['point']) == 0:
			steps_week.append(0)
		else:
			steps_week.append(bucket['dataset'][0]['point'][0]['value'][0]['intVal'])


	return render_template("steps.html", steps_today=steps_today, steps_last_week=sum(steps_week))




if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
app.run()