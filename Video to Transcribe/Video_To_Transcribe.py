 import json
import boto3
import urllib.parse
import uuid

def lambda_handler(event, context):
    # Retrieve the S3 bucket and key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    # Check if the object is in the "videos_to_transcript" folder
    if not object_key.startswith('videos_to_transcript/'):
        return {
            'statusCode': 200,
            'body': json.dumps('Object is not in the "videos_to_transcript" folder. Skipping.')
        }
    
    # Initialize the Amazon Transcribe client
    transcribe = boto3.client('transcribe')
    
    # Generate a unique job name for the transcription using a UUID
    job_name = str(uuid.uuid4()) + '-transcription'  # Append '-transcription' to the UUID for clarity
    
    # Define the S3 URI for the video file
    media_uri = 's3://' + bucket_name + '/' + object_key
    
    # Define the S3 bucket name to save the transcription output
    output_bucket = 'myvideotranscriptsbucket'
    
    # Start the transcription job
    response = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat=object_key.split('.')[-1],  # Extract the file format
        LanguageCode='en-US',  # Specify the language of the audio
        OutputBucketName=output_bucket,  # Save the transcript to the specified bucket
        Settings={
            'ShowSpeakerLabels': False  # Disable speaker labels
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Transcription job started successfully.')
    }