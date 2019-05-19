import boto3
import sys
import numpy as np
import random 
import time
# endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
##Remember to put the AWS credential in ~/.aws/credential like below:
#######
#[default]
#aws_access_key_id = XXXXX
#aws_secret_access_key = XXXXXX
client = boto3.client('mturk',endpoint_url = endpoint_url,region_name='us-east-1')
#Number of participants
number_participants=int(sys.argv[1])
result_hits= client.list_hits()
number_of_parallel_hits=len(result_hits['HITs'])
vector_completed_experiments = np.zeros(number_of_parallel_hits)

# Check that all the experiments have been completed 
while np.mean(vector_completed_experiments) != number_participants:
	result_hits= client.list_hits()
	number_of_parallel_hits=len(result_hits['HITs'])
	vector_completed_experiments=np.zeros(number_of_parallel_hits)
	for i in range(number_of_parallel_hits):
		hits_completed=int(result_hits['HITs'][i]['NumberOfAssignmentsCompleted'])
		vector_completed_experiments[i]=hits_completed
		if hits_completed != number_participants:
			##Checking if it is necessary to extend the HIT (Available and Pending HIT  should be set to zero for extending)
			if int(result_hits['HITs'][i]['NumberOfAssignmentsAvailable']) == 0 and int(result_hits['HITs'][i]['NumberOfAssignmentsPending']) == 0:
			   #There is a little bit of lag when checking whether the HIT has been completed, waiting  30 second to avoid this issue
			   time.sleep(30) 
			   result_hits= client.list_hits()
			   hits_completed=int(result_hits['HITs'][i]['NumberOfAssignmentsCompleted'])
			   if hits_completed <  number_participants and hits_completed > 0:
				   hit = result_hits['HITs'][i]['HITId']
				   #The request token should always be unique for each additional assignment
				   request_token= 'Request_{}_{}_{}'.format(hit,random.randint(1,100000),hits_completed)
				   print("Extending the HIT for the following ID: {}".format(hit))
				   client.create_additional_assignments_for_hit(HITId = hit, NumberOfAdditionalAssignments=1, UniqueRequestToken=request_token)

	#Sleep for 10 minutes..
	print("Sleeping for 10 minutes...")
	time.sleep(600) 
	print("Completed participants:",vector_completed_experiments)

