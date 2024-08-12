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
2. Google Cloud SDK installed and authenticated.
3. Necessary IAM permissions:
   - `roles/compute.admin` to manage disks and snapshots.
   - `roles/cloudfunctions.developer` to deploy Cloud Functions.
   - `roles/cloudscheduler.admin` to manage Cloud Scheduler.



## HTTP Request Headers

Below are the details of the HTTP request headers used in Scheduler:

| **Name**       | **Value**            |
|----------------|-----------------------|
| Content-Type   | application/json      |
| User-Agent     | Google-Cloud-Scheduler|



## References

For a detailed example of creating snapshots in GCP using Python, refer to the official [GCP documentation](https://cloud.google.com/compute/docs/samples/compute-snapshot-create?hl=en)
