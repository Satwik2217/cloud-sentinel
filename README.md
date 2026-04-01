---
title: Cloud Sentinel
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
tags:
- openenv
---

# 🛡️ Cloud Sentinel: Autonomous Cloud Governance

**Cloud Sentinel** is a high-fidelity simulation environment designed for training AI agents in **Cloud FinOps** and **Cybersecurity Governance**. It challenges agents to manage a dynamic fleet of cloud resources, balancing the "Operational Tension" between cost optimization and security compliance.

Built to the **OpenEnv v1.0** specification for the **Meta OpenEnv Hackathon**.

---

## 🎯 The Problem: Cloud Waste & Vulnerability
In modern infrastructure, "Zombie Resources" (idle assets) cost enterprises billions annually, while unencrypted or public-facing data leads to catastrophic breaches. **Cloud Sentinel** provides a sandbox where agents learn to prune waste without causing production outages.

## 🛠️ Environment Specification

### **Observation Space**
The agent receives a structured JSON object containing:
* **Resources**: A list of 10 assets (Servers, Databases, Storage) with real-time `cpu_usage`, `cost_per_hour`, and security flags (`is_public`, `is_encrypted`).
* **Financial State**: `total_monthly_cost` (Projected 720-hour burn).
* **Compliance State**: `security_score` (0-100 heuristic).

### **Action Space (Discrete)**
* `terminate`: Deletes a resource. (High reward for idle, heavy penalty for active).
* `encrypt`: Enables encryption on a storage/DB asset.
* `revoke_access`: Removes public internet exposure.

---

## 🏆 Defined Tasks & Grading
| Task ID | Name | Difficulty | Objective |
| :--- | :--- | :--- | :--- |
| `easy-zombie-hunt` | Zombie Hunter | Easy | Terminate at least 1 idle resource (CPU < 10%). |
| `medium-security-sweep` | Security Hardening | Medium | Achieve a Security Score of 100.0. |
| `hard-budget-architect` | Total Optimization | Hard | Cost < $500 AND Security = 100. |

---

## 🚀 Quick Start (Local Docker)

### **1. Build & Run Environment**
```bash
docker build -t cloud-sentinel .
docker run -p 8000:8000 cloud-sentinel