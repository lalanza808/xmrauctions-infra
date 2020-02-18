#!/usr/bin/env python3

from getpass import getpass


cloudtrail_bucket = raw_input('Cloudtrail bucket name? ')
access_key = getpass('IAM Access Key? ')
secret_key = getpass('IAM Secret Key? ')

env_data = "CLOUDTRAIL_BUCKET={}\nAWS_ACCESS_KEY_ID={}\nAWS_SECRET_ACCESS_KEY={}".format(
    cloudtrail_bucket, access_key, secret_key
)

with open('.env', 'w') as f:
    f.write(env_data)

print('[+] .env file created with provided secrets.')
