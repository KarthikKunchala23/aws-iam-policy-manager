# AWS IAM Policy Manager

## Overview

AWS IAM Policy Manager is a Python-based automation tool that generates, validates, stores, and synchronizes AWS IAM Managed Policies using YAML configuration files and Jinja2 templates.

The project is designed to eliminate repetitive IAM policy creation by following a configuration-driven approach. Instead of manually writing JSON policies, developers define permissions in YAML files, and the application generates standardized IAM policy documents automatically.

This project follows a modular, object-oriented architecture inspired by production-grade backend applications.

---

## Features

* Generate AWS IAM Managed Policies from YAML configurations
* Render policy documents using Jinja2 templates
* Store generated policies locally as JSON
* Validate configuration before policy generation
* Process multiple microservices automatically
* Modular and scalable Python project structure
* Structured logging for troubleshooting
* Ready for AWS IAM synchronization (next milestone)

---

## Project Structure

```text
aws-iam-policy-manager/

├── configs/
│   └── services/
│       ├── orders.yaml
│       ├── carts.yaml
│       └── catalog.yaml
│
├── templates/
│   └── managed_policy.j2
│
├── policies/
│   └── generated/
│
├── src/
│   └── iam_policy_manager/
│       ├── config/
│       ├── managers/
│       ├── models/
│       ├── services/
│       ├── utils/
│       └── main.py
│
└── tests/
```

---

## Architecture

```
YAML Configuration
        │
        ▼
Configuration Loader
        │
        ▼
Template Service
        │
        ▼
Policy Dataclass
        │
        ▼
File Service
        │
        ▼
Generated JSON Policies
        │
        ▼
(AWS IAM Synchronization - Upcoming)
```

---

## Technologies Used

* Python 3.12
* AWS IAM
* boto3
* Jinja2
* PyYAML
* pathlib
* logging
* dataclasses

---

## Current Workflow

1. Read YAML configuration.
2. Validate mandatory fields.
3. Render IAM policy using Jinja2.
4. Create a Policy model.
5. Generate IAM policy JSON.
6. Save policies to the local repository.
7. Process multiple services automatically.

---

## Example Configuration

```yaml
policy_name: orders-dynamodb-policy

description: IAM policy for Orders Service

template: managed_policy.j2

actions:
  - dynamodb:GetItem
  - dynamodb:PutItem

resources:
  - arn:aws:dynamodb:ap-south-1:123456789012:table/orders
```

---

## Example Generated Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PolicyStatement",
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:ap-south-1:123456789012:table/orders"
            ]
        }
    ]
}
```

---

## Upcoming Enhancements

* AWS IAM Policy Synchronization
* Policy Version Management
* Automatic Drift Detection
* Policy Comparison Engine
* HTML and JSON Reports
* Unit Test Coverage
* CLI Commands
* GitHub Actions CI/CD Pipeline

---

## Learning Outcomes

This project helped strengthen knowledge in:

* Python Backend Development
* Object-Oriented Programming
* Project Architecture
* Configuration-Driven Development
* AWS IAM APIs
* Template Engines
* JSON Processing
* Logging and Exception Handling
* Modular Software Design

---

## Author

**Karthik Raju Kunchala**

AWS DevOps & Platform Engineer

Building automation for cloud infrastructure, platform engineering, Kubernetes, Terraform, Python, and AWS.
