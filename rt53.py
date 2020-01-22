import boto3
import sys
import logging
import pprint
import argparse
import pymysql
import socket

def assume_role(account_number):
    """assume role for sts to access aws"""

    client = boto3.client('sts')
    role_arn = 'arn:aws:iam::' + account_number + ':role/banner-assume-role'
    try:
        response = client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='jenkins-dns-update'
        )

        aws_access_key = response['Credentials']['AccessKeyId']
        aws_secret_key = response['Credentials']['SecretAccessKey']
        aws_session_token = response['Credentials']['SessionToken']

        return aws_access_key, aws_secret_key, aws_session_token

    except ClientError as s:
        logging.warning('could not access 10024 DNS account with assume role: {}'.format(s))
        sys.exit(1)


def sql_conn_s2s(db_user, db_passwd, db_host):
    """Establishes SQL connection to network DB"""
    try:
        connection = pymysql.connect(host=db_host, user=db_user, passwd=db_passwd, db="network")
    except Exception as e:
        logging.fatal("Couldn't connect to S2S database: %s" % e)
        sys.exit(1)
    return connection


def get_account_info_from_db(shortname, zone_name):
    """"Queries network DB for all customers in the accounts table and returns a list of dicts """

    # setting variable for database connection to grab account info
    connection = sql_conn_s2s(args.db_user, args.db_password, 'cloudops-secure-cluster.cluster-cyabrfubwypz.us-east-1.rds.amazonaws.com')
    # Setting the cursor
    cursor = connection.cursor()
    # execute the SQL query using execute() method.
    cursor.execute("""SELECT account_number, region FROM accounts WHERE shortname=%s""", [shortname])
    # Fetching all customer record from the DB
    columns = cursor.description
    cust_data = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    return cust_data


def main(acc_num, region, zone_name, check_flag):

    # setting aws credentials from sts assume role function
    sts_creds = assume_role(acc_num)
    credentials = {
        'aws_access_key_id': sts_creds[0],
        'aws_secret_access_key': sts_creds[1],
        'aws_session_token': sts_creds[2],
    }

    # Getting all the ELB values from that customer env
    dns_client = boto3.client('route53', **credentials)
    response_dns = dns_client.list_resource_record_sets(HostedZoneId='Z3CYIS02AZBCOO')
    print(response_dns)
	
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gather information of hosted zone to change cname type to alias')
    parser.add_argument('--short-name', dest='short_name', default=None, help='Argument for collecting shortname')
    parser.add_argument('--dns-zone', dest='dns_zone', default=None, help='Argument for collecting dns zone')
    parser.add_argument('--db-user', dest='db_user', default='site2siteuser', required=False,help='DB user for database with Site2Site information etc')
    parser.add_argument('--db-password', dest='db_password', required=True, help='DB password for database with Site2Site information etc')
    parser.add_argument('--db-host', dest='db_host', default='cloudops-secure-cluster.cluster-cyabrfubwypz.us-east-1.rds.amazonaws.com', required=False, help='DB host for database with Site2Site information etc')
    parser.add_argument('--check-flag', dest='check_dns_flag', default='', required=True, help='Flag for when to execute actual update to DNS.')
    args = parser.parse_args()

    shortname = args.short_name
    zone_name = args.dns_zone    
    check_flag = args.check_dns_flag
    cust_data = get_account_info_from_db(shortname, zone_name)
    for value in cust_data:
        acc_num = value['account_number']
        region = value['region']

    # passing the account number, regin and zone name to the main function
    main(acc_num, region, zone_name, check_flag)
