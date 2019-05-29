
###################################################
####  Connexion avec les variables d'environnement
###################################################

import boto3 as boto

"""
# via the aws Client
client = boto.client('s3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    aws_session_token=SESSION_TOKEN,
)

# Or via the Session
session = boto.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    aws_session_token=SESSION_TOKEN,
)
"""

###################################################
####  Connexion avec le fichier credentials
###################################################

client = boto.client('s3')
# session = boto.Session('s3')

####################################################
####    Create bucket Komeos
####################################################

bucket = client.create_bucket(Bucket='komeos_bucket')
print("ici")

####################################################
####    Display buckets
####################################################

# Call S3 to list current buckets
response = client.list_buckets()

# Get a list of all bucket names from the response
buckets = [bucket['Name'] for bucket in response['Buckets']]

# Print out the bucket list
print("Bucket List: " + str(buckets))
exit()

####################################################
####   Upload files
####################################################

LocalFileList = [ 
   # '../front_end/static/html/doc_1',
    '../front_end/static/summary/doc_1.json',
    '../front_end/static/table/doc_1.json' 
]
docname = "SG_EF_2019"

bucket_name = 'komeos_bucket'
for localfile in LocalFileList :
    pathsplit = localfile.split('/')
    print(pathsplit)
    S3filename = docname + "_" + pathsplit[3] + "_" + pathsplit[4]
    print(S3filename)
    client.upload_file(localfile, bucket_name, S3filename)
