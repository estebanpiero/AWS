import boto3
import json

def get_firewall_domain_list_id(r53resolver_client, list_name):
    try:
        paginator = r53resolver_client.get_paginator('list_firewall_domain_lists')
        for page in paginator.paginate():
            for domain_list in page['FirewallDomainLists']:
                if domain_list['Name'] == list_name:
                    return domain_list['Id']
        raise ValueError(f"Firewall domain list '{list_name}' not found")
    except Exception as e:
        raise Exception(f"Error getting firewall domain list ID: {str(e)}")

def lambda_handler(event, context):
    try:
        BUCKET_NAME = "S3-BUCKET-NAME"
        DOMAIN_LIST_NAME = "DOMAIN_LIST_NAME"
        
        key = event['Records'][0]['s3']['object']['key']
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        if source_bucket != BUCKET_NAME:
            raise ValueError(f"Unexpected bucket: {source_bucket}")
        
        s3_client = boto3.client('s3')
        r53resolver_client = boto3.client('route53resolver')
        
        firewall_domain_list_id = get_firewall_domain_list_id(r53resolver_client, DOMAIN_LIST_NAME)
        
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        domains = [domain.strip() for domain in file_content.splitlines() if domain.strip()]
        
        response = r53resolver_client.update_firewall_domains(
            FirewallDomainListId=firewall_domain_list_id,
            Operation='REPLACE',
            Domains=domains
        )
        
        print(f"Successfully updated DNS Firewall Domain List with {len(domains)} domains")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully updated DNS Firewall Domain List',
                'domainsUpdated': len(domains)
            })
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error updating DNS Firewall Domain List',
                'message': error_message
            })
        }