---
date: 2026-07-06
categories:
  - GKE
tags:
  - GKE
  - GCP
  - Kubernetes
  - Reservation
slug: gke-zone-reservation
---

# Setting Up Reservations for Per-Zone Availability: An Operations Log

While operating a GKE cluster, I ran into a situation where StatefulSets could not be rescheduled because a specific zone ran out of node stock. Here I'm recording how I solved it by adopting Reservations, along with a node pool upgrade problem I newly encountered along the way.

## Current Setup

- Standard mode cluster, with a maintenance window of 6 hours each on Saturday–Sunday
- Vertical Pod Autoscaling (VPA) and Node Auto-Provisioning (NAP) are not used
- Node auto-upgrade is enabled

## Problem 1. Nodes Disappeared Due to Zone Stockout

A temporary shortage of n4-standard-2 nodes occurred in zone c of us-west1.

As luck would have it, the stockout coincided with nodes being replaced by an auto-upgrade, so the zone-c nodes disappeared, and the StatefulSet pods using Grafana and PVCs (loki-backend, tempo-ingester, loki-write, prometheus-kube-prometheus-stack-prometheus) were failing to get rescheduled.

Because PVCs are zone-bound, if a zone has no nodes, the pods that were using disks in that zone cannot move to another zone and are left stuck in Pending.

## Solution 1. Use Reservations

To secure capacity for the nodes ahead of time, I switched to using [Reservations](https://cloud.google.com/compute/docs/instances/reservations-overview).

One thing to watch out for here: a reservation can be consumed not only by GKE but also by other services (VMs, etc.) in the same project. Under the default setting (an open reservation), any VM with a matching machine spec can consume the reserved capacity. Right now we only run GKE on GCP, but if some other service comes along and its instances grab the reserved capacity first, the same problem would come right back... To prevent this, I configured things as follows:

1. When creating the reservation, set the "Use with VM instance" option to **"Select specific reservation"**, and
2. Create a separate node pool that uses only reservations, pointing it exclusively at the reservation created in step 1.

This way the reservation becomes dedicated to this node pool, and no other workload can take its capacity.

Currently, the PRD cluster has 8 nodes total across 3 zones in use, so I simply created one reservation per zone.

## Problem 2. The Reserved Node Pool Doesn't Upgrade During Maintenance

The reservation solved the availability problem, but then a new one appeared: the node pool using the reservation was not being auto-upgraded during the maintenance window.

## Solution 2. Change max_surge to 0

Digging into the cause, the total capacity (reservation capacity) and current usage matched exactly in each zone, so the upgrade could not proceed with max_surge=1, which requires spinning up an extra surge node — and the upgrade was just stuck (this setting had been carried over as-is from the previous node pool). Since no capacity outside the reservation can be used, the surge approach itself — bringing up a new node while keeping the existing ones — is simply impossible in this situation.

- Before: max_surge=1 / max_unavailable=1
- After: max_surge=0 (max_unavailable=1)

With max_surge=0, instead of bringing up a new node first, existing nodes are taken down one at a time and a new node comes up in each one's place, so the upgrade proceeds within the reserved capacity. There is a trade-off — the node count temporarily drops by one during the upgrade — but in a configuration that fills its per-zone reservations to capacity, I judged this to be the right approach.

## Summary

- Zone-level stockouts really do happen, and StatefulSets that use PVCs are especially vulnerable because they are tied to a zone.
- When securing capacity with reservations, use the "Select specific reservation" + dedicated node pool combination so other services cannot steal the capacity.
- A node pool that fully consumes its reserved capacity cannot do surge upgrades, so max_surge must be set to 0 for auto-upgrades to work properly.
