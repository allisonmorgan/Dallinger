#!/bin/bash
#app ID (dallinger)
appname=$1
#number of total participants in the experiment
num_participants=$2

#Extract from config.txt if it is sandbox or live option
mode_experiment=`grep "mode" config.txt | awk -F "=" '{print $2}' | sed 's/ //g'`

rm -r ./data/*
rm ./data/*
#two indexes: one for the real participants (np) and the other index just in case of failure with some participants
dallinger export --app $appname
unzip -o ./data/*.zip
l=`wc -l data/participant.csv | awk '{print $1}'`
np=`awk -F "," '{ print $8}' data/node.csv | tail -n +2 | grep  -c "f"`
np=$((np-1))




echo "Total number of current participants: $np"
while [ $np -lt $num_participants ]
do
	dallinger export --app $appname
	unzip -o ./data/*.zip
	current_size=`wc -l data/participant.csv  | awk '{print $1}'`

	#the status can be 't' or 'f'
	status_participant=`awk -F "," '{print $8}' data/node.csv | awk 'NR == $((l+1))'`

	#if there is a failure with the last participant then update the counter l
	if [ "$status_participant" == "t" ]
	then
		l=$((l+1))
	fi
	echo "total number of partipants: $((current_size-1)) --- l : $l"
	#checking the lines of the file participant.csv for extending the HIT
	if (( $current_size == $l ))
	then
		echo "sleeping for 5 minutes..."
		sleep 300
	else
			echo "Extending the HITs"
			python boto3_extension.py $((np+1)) $mode_experiment
			np=$((np+1))
			l=$((l+1))
	fi
	rm -r ./data/*
done