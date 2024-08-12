# google-cloud-disk-snapshot-automation

## Overview

This project provides a Python Cloud Function that creates snapshots for all disks in a Google Cloud Platform (GCP) project. The function is triggered by an HTTP request using the POST method, which is scheduled through Google Cloud Scheduler.

## Features

- Creates snapshots for all disks in a specified GCP project.
- Uses Google Cloud Functions to handle the snapshot creation process.
- Triggered via an HTTP POST request.
- Scheduled using Google Cloud Scheduler for regular execution.

## Prerequisites

Before you start, ensure you have the following:

1. A Google Cloud Platform project.
2. **Cloud Function Deployment:**
    * A Python Cloud Function deployed in your GCP project. Refer to the project code for deployment instructions.
3. Necessary IAM permissions assigned to the service account used by the Cloud Function:
   - `roles/compute.admin` to manage disks and snapshots.
   - `roles/cloudfunctions.developer` to deploy Cloud Functions.
   - `roles/cloudscheduler.admin` to manage Cloud Scheduler.



## HTTP Request Headers

Below are the details of the HTTP request headers used in Scheduler:

| **Name**       | **Value**            |
|----------------|-----------------------|
| Content-Type   | application/json      |
| User-Agent     | Google-Cloud-Scheduler|

**Note:** The Cloud Function expects a JSON object in the request body containing Project ID and Zone. 
Refer `requestBody.json` file 

## References

For a detailed example of creating snapshots in GCP using Python, refer to the official [GCP documentation](https://cloud.google.com/compute/docs/samples/compute-snapshot-create?hl=en)
