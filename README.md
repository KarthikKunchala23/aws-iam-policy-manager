# AWS IAM Policy Manager

A Python-based, configuration-driven automation tool for generating, validating, storing, comparing, and synchronizing AWS IAM Managed Policies.

The tool uses a **single YAML configuration file** to define which IAM policies belong to which teams. Policy documents are maintained as reusable JSON/Jinja2 templates containing placeholders, while Python resolves mappings, renders the final policy documents, stores them locally, and synchronizes them with AWS IAM.

The project is designed using a modular, object-oriented architecture inspired by production-grade Python backend applications.

---

## Overview

Managing IAM policies manually across multiple teams and environments can become repetitive and error-prone.

AWS IAM Policy Manager solves this by separating:

* **What policies should exist** → YAML configuration
* **How policies should look** → JSON/Jinja2 templates
* **Dynamic values** → mappings and runtime AWS information
* **Policy generation** → Python services
* **Local policy storage** → FileService
* **AWS synchronization** → AWSIAMService
* **Policy comparison** → ComparisonService

The overall concept is:

```text
                  config.yaml
                       │
                       ▼
                Configuration Loader
                       │
                       ▼
                  Policy Manager
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Team Selection  Mappings    Templates
          │            │            │
          └────────────┼────────────┘
                       ▼
                 Policy Renderer
                       │
                       ▼
                Generated Policy
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Local JSON            AWS IAM
                                 │
                                 ▼
                       Compare Local vs AWS
                                 │
                         ┌───────┴───────┐
                         ▼               ▼
                       Same          Different
                         │               │
                         ▼               ▼
                        Skip          Update
```

---

# Features

* Configuration-driven IAM policy management
* Single YAML configuration file
* Team-based policy ownership
* Reusable policy templates
* Jinja2 template rendering
* Dynamic placeholder substitution
* AWS account ID discovery using AWS STS
* Automatic local policy generation
* Generated policy storage as JSON
* AWS IAM Managed Policy creation
* AWS IAM policy synchronization
* Local-vs-AWS policy comparison
* Policy normalization before comparison
* Idempotent synchronization
* AWS policy version management
* Structured logging
* Modular service-oriented architecture
* Object-oriented Python design
* Easy extension for additional AWS services and policy types

---

# Key Design Principle

The project follows a simple separation of responsibility:

```text
YAML
 │
 │ Defines desired configuration
 ▼
Python
 │
 │ Resolves configuration and mappings
 ▼
Template
 │
 │ Defines policy structure
 ▼
Rendered Policy
 │
 ├──────────────► Local JSON
 │
 └──────────────► AWS IAM
                       │
                       ▼
                  Comparison
                       │
                  ┌────┴────┐
                  ▼         ▼
                 SAME    DIFFERENT
                  │         │
                  ▼         ▼
                 SKIP     UPDATE
```

The YAML configuration represents the **desired state**, while AWS IAM represents the **actual state**.

Python acts as the reconciliation layer between the two.

---

# Architecture

```text
                         ┌──────────────────┐
                         │   config.yaml    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Config Loader   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Policy Manager  │
                         └────────┬─────────┘
                                  │
                     ┌────────────┼────────────┐
                     │            │            │
                     ▼            ▼            ▼
               Team Config    Mappings     Templates
                     │            │            │
                     └────────────┼────────────┘
                                  ▼
                         ┌──────────────────┐
                         │ Policy Renderer  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Policy Model    │
                         └────────┬─────────┘
                                  │
                       ┌──────────┴──────────┐
                       │                     │
                       ▼                     ▼
                FileService           AWSIAMService
                       │                     │
                       ▼                     ▼
                Local JSON             AWS IAM
                                             │
                                             ▼
                                    AWS Policy Document
                                             │
                                             ▼
                                    ComparisonService
                                             │
                                  ┌──────────┴──────────┐
                                  ▼                     ▼
                               Identical             Changed
                                  │                     │
                                  ▼                     ▼
                                SKIP                 UPDATE
```

---

# Project Structure

```text
aws-iam-policy-manager/
│
├── configs/
│   └── config.yaml
│
├── templates/
│   └── policies/
│       ├── orders-policy.json
│       ├── payments-policy.json
│       └── ...
│
├── policies/
│   └── generated/
│       ├── orders/
│       │   └── orders-policy.json
│       ├── payments/
│       │   └── payments-policy.json
│       └── ...
│
├── src/
│   └── iam_policy_manager/
│       │
│       ├── config/
│       │   └── loader.py
│       │
│       ├── managers/
│       │   └── policy_manager.py
│       │
│       ├── models/
│       │   └── policy.py
│       │
│       ├── services/
│       │   ├── aws_iam_service.py
│       │   ├── comparison_service.py
│       │   ├── file_service.py
│       │   └── template_service.py
│       │
│       ├── utils/
│       │
│       └── main.py
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

# Configuration Model

The project uses a **single YAML configuration file**.

The YAML defines the relationship between:

```text
Team
 │
 └── Policies
```

For example:

```yaml
policy_generators:

  - name: orders

    team: orders

    policies:
      - name: orders-policy
        template: orders-policy.json
```

Another team can have its own policies:

```yaml
policy_generators:

  - name: orders
    team: orders
    policies:
      - name: orders-policy
        template: orders-policy.json

  - name: payments
    team: payments
    policies:
      - name: payments-policy
        template: payments-policy.json
```

The important design principle is:

```text
orders
   │
   └── orders-policy

payments
   │
   └── payments-policy
```

A policy assigned to `orders` is processed only for the `orders` team.

This prevents the same policy from accidentally being generated for every team.

---

# Policy Templates

Policy templates contain the actual IAM policy structure.

Example:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "OrdersPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::${account_id}-${environment}-${team}/*"
            ]
        }
    ]
}
```

The template contains placeholders such as:

```text
${account_id}
${environment}
${region}
${team}
```

Python resolves these placeholders before the policy is sent to AWS.

---

# Mapping Resolution

Mappings provide dynamic values used during policy rendering.

For example:

```yaml
mappings:

  environment: dev

  region: ap-south-1
```

The AWS account ID can be obtained dynamically using AWS STS:

```text
AWS STS
   │
   ▼
GetCallerIdentity
   │
   ▼
AWS Account ID
```

The final rendering context may look like:

```python
{
    "account_id": "123456789012",
    "environment": "dev",
    "region": "ap-south-1",
    "team": "orders"
}
```

The template:

```text
arn:aws:s3:::${account_id}-${environment}-${team}/*
```

becomes:

```text
arn:aws:s3:::123456789012-dev-orders/*
```

---

# End-to-End Workflow

## 1. Load configuration

Python reads:

```text
configs/config.yaml
```

and converts the YAML into Python dictionaries and lists.

```text
YAML
 ↓
PyYAML
 ↓
Python dict/list objects
```

---

## 2. Process policy generators

The `PolicyManager` loops through the configured policy generators.

```python
for generator in config.get("policy_generators", []):
```

Each generator represents a policy generation context.

---

## 3. Render policies

The `render_policy()` service:

* Reads the configured template
* Builds the rendering context
* Resolves mappings
* Substitutes placeholders
* Creates the Policy model

The result contains information such as:

```text
Policy
 ├── policy_name
 ├── document
 ├── target_policy_path
 └── context
```

---

## 4. Save generated policy

The generated policy is saved locally as JSON.

```text
policies/generated/
```

This provides a local representation of the desired IAM policy.

---

# AWS IAM Synchronization

After generating the policy locally, the `PolicyManager` calls:

```python
sync_policy_to_aws(policy)
```

The synchronization process is:

```text
Generated Local Policy
        │
        ▼
Does policy exist in AWS?
        │
   ┌────┴────┐
   │         │
  NO        YES
   │         │
   ▼         ▼
CREATE    Get AWS Policy
             │
             ▼
       Compare Policies
             │
       ┌─────┴─────┐
       │           │
      SAME      DIFFERENT
       │           │
       ▼           ▼
      SKIP       UPDATE
```

---

# Create Flow

If the policy does not exist:

```text
PolicyManager
      │
      ▼
AWSIAMService.policy_exists()
      │
      ▼
False
      │
      ▼
AWSIAMService.create_policy()
      │
      ▼
AWS IAM Managed Policy
```

The policy is created in AWS.

---

# Update Flow

If the policy already exists:

```text
AWS IAM
   │
   ▼
Get Policy
   │
   ▼
Get Default Version ID
   │
   ▼
Get Policy Version
   │
   ▼
Current AWS Policy Document
```

The AWS policy document is then compared with the locally generated policy.

---

# Policy Comparison

The `ComparisonService` determines whether the local and AWS policies are identical.

```python
comparison_service.compare(
    local_policy,
    aws_policy
)
```

Before comparison, policies are normalized.

Normalization handles differences such as list ordering.

For example:

### Local

```json
"Action": [
    "s3:GetObject",
    "s3:PutObject"
]
```

### AWS

```json
"Action": [
    "s3:PutObject",
    "s3:GetObject"
]
```

These represent the same permissions.

The comparison service sorts the lists before comparing them.

It also sorts JSON dictionary keys to make the comparison deterministic.

---

# Comparison Logic

```text
             Local Policy
                  │
                  ▼
             normalize()
                  │
                  ▼
             JSON String
                  │
                  │
                  │ compare
                  │
                  ▼
             JSON String
                  ▲
                  │
             normalize()
                  │
                  ▲
              AWS Policy
```

If the normalized documents are equal:

```text
True
 ↓
Policy is already synchronized
 ↓
SKIP
```

If they are different:

```text
False
 ↓
Policy has changed
 ↓
Create new AWS policy version
```

---

# Idempotent Synchronization

The tool is designed to be idempotent.

For example, running:

```bash
python -m src.iam_policy_manager.main
```

multiple times should not create unnecessary AWS policy versions when there are no changes.

### First run

```text
Local Policy
     ↓
AWS Policy doesn't exist
     ↓
CREATE
```

### Second run

```text
Local Policy
     ↓
AWS Policy exists
     ↓
Compare
     ↓
Same
     ↓
SKIP
```

### After changing the template

```text
Local Policy
     ↓
AWS Policy exists
     ↓
Compare
     ↓
Different
     ↓
CREATE NEW VERSION
```

This is similar to the desired-state reconciliation model used by infrastructure-as-code tools.

---

# Core Components

## PolicyManager

The main orchestration layer.

Responsibilities:

* Load configuration
* Process policy generators
* Render policies
* Save policies locally
* Synchronize policies with AWS
* Coordinate comparison and AWS operations

The manager does not implement the low-level AWS API operations itself.

---

## Config Loader

Responsible for:

```text
config.yaml
     ↓
Python objects
```

It loads and validates the configuration.

---

## Template Service

Responsible for:

```text
Template
+
Context
 ↓
Rendered Policy
```

It handles policy generation and placeholder substitution.

---

## FileService

Responsible for storing generated policies locally.

```text
Policy object
     ↓
FileService
     ↓
JSON file
```

---

## AWSIAMService

Responsible for communication with AWS IAM.

Typical responsibilities include:

* Get AWS account ID
* Build policy ARN
* Check whether a policy exists
* Create IAM policies
* Retrieve IAM policies
* Retrieve policy versions
* Retrieve policy documents
* Create new policy versions

The AWS-specific boto3 logic is isolated inside this service.

---

## ComparisonService

Responsible for comparing:

```text
Local Policy
     vs
AWS Policy
```

It:

* Normalizes policies
* Sorts relevant lists
* Sorts JSON keys
* Performs deterministic comparison
* Returns `True` or `False`

---

# Technologies Used

* Python 3.12
* AWS IAM
* AWS STS
* boto3
* Jinja2
* PyYAML
* JSON
* pathlib
* logging
* dataclasses
* pytest

---

# Installation

Clone the repository:

```bash
git clone <repository-url>

cd aws-iam-policy-manager
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# AWS Authentication

The application uses `boto3`, so AWS credentials must be available through one of the standard AWS credential mechanisms.

For example:

```bash
aws configure
```

Verify the current identity:

```bash
aws sts get-caller-identity
```

The application uses AWS STS to determine the AWS account ID.

The IAM permissions required by the executing identity depend on the operations enabled by the tool.

Typical permissions include:

```text
iam:GetPolicy
iam:GetPolicyVersion
iam:CreatePolicy
iam:CreatePolicyVersion
iam:ListPolicyVersions
iam:DeletePolicyVersion
```

---

# Running the Application

Run the application using the project's configured entry point.

For example:

```bash
python -m src.iam_policy_manager.main
```

If the application accepts a configuration file argument:

```bash
python -m src.iam_policy_manager.main config.yaml
```

The exact command can be adjusted according to the CLI implementation.

---

# Example Execution

A typical execution looks like:

```text
INFO - Processing configuration configs/config.yaml

INFO - Processing policy generator 'orders'

INFO - Generated policy 'orders-policy'
      with context:
      {
          'team': 'orders',
          'environment': 'dev',
          'region': 'ap-south-1'
      }

INFO - Generated policy saved at:
      policies/generated/orders/orders-policy.json

INFO - Policy 'orders-policy' exists in AWS IAM.
      Checking for changes.

INFO - Policy 'orders-policy' is already up to date.
      No AWS update required.
```

If the policy has changed:

```text
INFO - Policy 'orders-policy' exists in AWS IAM.
      Checking for changes.

INFO - Policy 'orders-policy' has changed.
      Creating new policy version.

INFO - Created new policy version 'v3'
      for policy 'orders-policy'
```

---

# Design Principles

## Configuration Driven

Policy behavior is controlled through YAML rather than hard-coded Python logic.

---

## Separation of Concerns

Each component has a specific responsibility:

```text
ConfigLoader
    ↓
Configuration

TemplateService
    ↓
Policy Generation

FileService
    ↓
Local Storage

ComparisonService
    ↓
Policy Comparison

AWSIAMService
    ↓
AWS IAM

PolicyManager
    ↓
Orchestration
```

---

## Reusable Templates

The same policy template can be reused with different contexts.

```text
Template
   +
Orders Context
   ↓
Orders Policy

Template
   +
Payments Context
   ↓
Payments Policy
```

---

## Desired State vs Actual State

The project follows a reconciliation model:

```text
Desired State
    │
    ▼
Generated Local Policy
    │
    │ compare
    ▼
Actual State
    │
    ▼
AWS IAM
```

The application only changes AWS when the actual state differs from the desired state.

---

# Future Enhancements

Potential future improvements include:

* Policy drift detection
* Policy validation against AWS IAM Access Analyzer
* Policy syntax validation
* AWS policy version cleanup
* Dry-run mode
* CLI commands
* Policy change reports
* HTML reports
* JSON reports
* Detailed synchronization summaries
* Unit and integration test coverage
* GitHub Actions CI/CD
* Multi-account AWS support
* Multi-environment support
* Policy approval workflow
* Policy rollback
* CloudTrail-based audit integration
* Terraform integration
* Policy dependency validation

---

# Testing

Unit tests can be added under:

```text
tests/
```

Important test areas include:

```text
Configuration loading
Template rendering
Mapping resolution
Policy generation
Policy normalization
Policy comparison
AWS policy existence checks
AWS policy synchronization
```

A particularly important test is:

```text
Local policy == AWS policy
        ↓
No new AWS version should be created
```

And:

```text
Local policy != AWS policy
        ↓
New AWS policy version should be created
```

---

# Learning Outcomes

This project provides practical experience with:

### Python

* Functions
* Classes
* Object-oriented programming
* Dataclasses
* Dictionaries and lists
* Exception handling
* Logging
* File handling
* JSON processing
* YAML processing
* Modular application architecture

### Backend Development

* Service-oriented design
* Separation of concerns
* Dependency relationships
* Configuration-driven applications
* Data transformation
* Validation
* State reconciliation

### AWS

* AWS IAM
* Managed Policies
* IAM Policy Versions
* AWS STS
* boto3
* AWS API integration
* AWS authentication
* IAM permissions

### DevOps / Platform Engineering

* Infrastructure automation
* Policy as Code
* Desired-state management
* Idempotency
* Drift detection concepts
* CI/CD integration
* Cloud security automation

---

# Current Architecture Summary

The complete application can be summarized as:

```text
                         ┌───────────────┐
                         │  config.yaml  │
                         └───────┬───────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │   Config Loader   │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │   Policy Manager  │
                       └─────────┬─────────┘
                                 │
                   ┌─────────────┼─────────────┐
                   │             │             │
                   ▼             ▼             ▼
                Teams        Mappings      Templates
                   │             │             │
                   └─────────────┼─────────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │  Template Service │
                       └─────────┬─────────┘
                                 │
                                 ▼
                         Generated Policy
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              File Service             AWS IAM Service
                    │                         │
                    ▼                         ▼
              Local JSON                AWS Policy
                                              │
                                              ▼
                                     Get AWS Document
                                              │
                                              ▼
                                     Comparison Service
                                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                                  SAME              DIFFERENT
                                    │                   │
                                    ▼                   ▼
                                  SKIP              UPDATE
```

---

# Author

**Karthik Raju Kunchala**

AWS DevOps & Platform Engineer

Focused on AWS, Kubernetes, Terraform, Python, DevOps automation, and cloud platform engineering.
