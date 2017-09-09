from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
import httplib2


import os
import time
import datetime

client_id = os.environ["GGL_ID"]
client_secret = os.environ["GGL_SECRET"]

scope = "https://www.googleapis.com/auth/fitness.activity.read"
flow = OAuth2WebServerFlow(client_id, client_secret, scope)

storage = Storage('credentials.dat')

# The get() function returns the credentials for the Storage object. If no
# credentials were found, None is returned.
credentials = storage.get()

# If no credentials are found or the credentials are invalid due to
# expiration, new credentials need to be obtained from the authorization
# server. The oauth2client.tools.run_flow() function attempts to open an
# authorization server page in your default web browser. The server
# asks the user to grant your application access to the user's data.
# If the user grants access, the run_flow() function returns new credentials.
# The new credentials are also stored in the supplied Storage object,
# which updates the credentials.dat file.
if credentials is None or credentials.invalid:
	credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())

# Create an httplib2.Http object to handle our HTTP requests, and authorize it
# using the credentials.authorize() function.
http = httplib2.Http()
http = credentials.authorize(http)

# The apiclient.discovery.build() function returns an instance of an API service
# object can be used to make API calls. The object is constructed with
# methods specific to the calendar API. The arguments provided are:
#   name of the API ('calendar')
#   version of the API you are using ('v3')
#   authorized httplib2.Http() object that can be used for API calls
service = build('fitness', 'v1', http=http)

#service = build('fitness', 'v1', developerKey=os.environ["GGL_ID"], developerSecret=os.environ["GGL_SECRET"])


# activities = service.users().sessions().list(userId="me")

# data = service.users().dataSources().list(userId="me")

# steps = service.users().dataSources().get(userId="me", dataSourceId="raw:com.google.step_count.cumulative:LGE:Nexus 5:9314b2d:Step Counter")


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
