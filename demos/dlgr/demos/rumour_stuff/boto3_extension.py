import boto3
import sys
import random 
import time


endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
client = boto3.client('mturk', endpoint_url = endpoint_url, region_name = 'us-east-1')
#take the hit of the most recent Heroku app
hit = client.list_hits()['HITs'][0]['HITId']
request_token= 'Request{}_{}_{}'.format(int(sys.argv[1]),hit,random.randint(1,1000))
print(hit,request_token)
#sleep for 5 minutes
time.sleep(300)
client.create_additional_assignments_for_hit(HITId = hit, NumberOfAdditionalAssignments=1, UniqueRequestToken=request_token) 