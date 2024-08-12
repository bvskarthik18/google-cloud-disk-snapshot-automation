from __future__ import annotations

import sys
from typing import Any, List
from datetime import datetime

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1

from flask import request, jsonify, make_response


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
    """
    Waits for the extended (long-running) operation to complete.

    If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
    try:
        result = operation.result(timeout=timeout)
    except Exception as e:
        print(f"Operation failed: {str(e)}", file=sys.stderr, flush=True)
        raise

    if operation.error_code:
        print(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
            file=sys.stderr,
            flush=True,
        )
        print(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        print(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)
        for warning in operation.warnings:
            print(f" - {warning.code}: {warning.message}", file=sys.stderr, flush=True)

    return result


def list_disks(project: str, zone: str | None = None, region: str | None = None) -> List[compute_v1.Disk]:
    """
    Lists disks in the specified project and zone or region.

    Args:
        project: project ID or project number of the Cloud project containing the disks.
        zone: name of the zone to list disks (for zonal disks).
        region: name of the region to list disks (for regional disks).

    Returns:
        List of Disk resources.
    """
    if zone:
        disk_client = compute_v1.DisksClient()
        disks = disk_client.list(project=project, zone=zone)
    elif region:
        region_disk_client = compute_v1.RegionDisksClient()
        disks = region_disk_client.list(project=project, region=region)
    else:
        raise ValueError("Either `zone` or `region` must be provided.")

    return list(disks)


def create_snapshot(
    project: str,
    disk_name: str,
    snapshot_name: str,
    *,
    zone: str | None = None,
    region: str | None = None,
    location: str | None = None,
    disk_project: str | None = None,
) -> compute_v1.Snapshot:
    """
    Create a snapshot of a disk.

    Args:
        project: project ID or project number of the Cloud project you want
            to use to store the snapshot.
        disk_name: name of the disk you want to snapshot.
        snapshot_name: name of the snapshot to be created.
        zone: name of the zone in which is the disk you want to snapshot (for zonal disks).
        region: name of the region in which is the disk you want to snapshot (for regional disks).
        location: The Cloud Storage multi-region or the Cloud Storage region where you
            want to store your snapshot.
            You can specify only one storage location. Available locations:
            https://cloud.google.com/storage/docs/locations#available-locations
        disk_project: project ID or project number of the Cloud project that
            hosts the disk you want to snapshot. If not provided, will look for
            the disk in the `project` project.

    Returns:
        The new snapshot instance.
    """
    if zone is None and region is None:
        raise RuntimeError("You need to specify `zone` or `region` for this function to work.")
    if zone is not None and region is not None:
        raise RuntimeError("You can't set both `zone` and `region` parameters.")

    if disk_project is None:
        disk_project = project

    if zone is not None:
        disk_client = compute_v1.DisksClient()
        disk = disk_client.get(project=disk_project, zone=zone, disk=disk_name)
    else:
        region_disk_client = compute_v1.RegionDisksClient()
        disk = region_disk_client.get(project=disk_project, region=region, disk=disk_name)

    snapshot = compute_v1.Snapshot()
    snapshot.source_disk = disk.self_link
    snapshot.name = snapshot_name
    if location:
        snapshot.storage_locations = [location]

    snapshot_client = compute_v1.SnapshotsClient()
    operation = snapshot_client.insert(project=project, snapshot_resource=snapshot)

    wait_for_extended_operation(operation, f"snapshot creation for {disk_name}")

    return snapshot_client.get(project=project, snapshot=snapshot_name)


def create_snapshots_for_all_disks(project: str, zone: str):
    disks = list_disks(project, zone=zone)
    current_month_name = datetime.now().strftime('%B').lower()  # Get current month name in lowercase
    current_year = datetime.now().strftime('%Y')  # Get current year

    for disk in disks:
        snapshot_name = f"{disk.name}-{current_month_name}-{current_year}-patching"  # Adjust snapshot naming as needed
        try:
            create_snapshot(project, disk.name, snapshot_name, zone=zone)
            print(f"Snapshot '{snapshot_name}' created successfully for disk '{disk.name}'.")
        except Exception as e:
            print(f"Snapshot creation failed for disk '{disk.name}': {str(e)}")


def main(request):
    """
    This function is triggered by an HTTP request.
    """
    # Check if request has a body
    if not request.get_data():
        return make_response(jsonify({"error": "Empty request body"}), 400)

    # Attempt to get JSON payload from request
    request_json = request.get_json(silent=True)

    # Validate request JSON
    if not request_json:
        return make_response(jsonify({"error": "Invalid JSON payload"}), 400)

    # Extract 'project' and 'zone' from the JSON payload
    project = request_json.get("project")
    zone = request_json.get("zone")

    # Log received payload
    print(f"Received request payload: project={project}, zone={zone}", file=sys.stderr)

    # Validate 'project' and 'zone'
    if not project or not zone:
        return make_response(jsonify({"error": "Missing 'project' or 'zone' in request"}), 400)

    try:
        # Call the function to create snapshots
        create_snapshots_for_all_disks(project, zone)
        return jsonify({"message": "Snapshots created successfully"}), 200
    except Exception as e:
        # Log the exception and return an error response
        print(f"Snapshot creation failed: {str(e)}", file=sys.stderr)
        return make_response(jsonify({"error": f"Snapshot creation failed: {str(e)}"}), 500)


