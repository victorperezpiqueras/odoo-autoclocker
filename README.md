# Odoo AutoClocker

![Static Badge](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=yellow)
![Static Badge](https://img.shields.io/badge/node-^20-green?logo=nodedotjs&logoColor=green)
![Static Badge](https://img.shields.io/badge/cloud-aws-yellow?logo=amazon&logoColor=yellow)
![Static Badge](https://img.shields.io/badge/infra-aws--cdk-red?logo=amazon&logoColor=red)
![Static Badge](https://img.shields.io/badge/erp-odoo-purple?logo=odoo&logoColor=purple)

AWS Lambda-based solution for automated employee attendance tracking in Odoo.

With a simple setup, this solution can automatically record employee attendance in Odoo in a daily manner, saving time
and reducing manual errors.

## Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- An AWS account, the AWS CLI and AWS-CDK installed
- Node.js 20+ (for AWS-CDK)
- An Odoo account with access to an Odoo instance

## Quick Start

### Clone and Install

```bash
git clone https://github.com/yourusername/odoo-attendance-tracker.git
cd odoo-attendance-tracker
poetry install
```

### Install AWS CDK

```bash
npm install -g aws-cdk
```

## AWS Setup

### Configure AWS CLI

```bash
aws configure
```

### Bootstrap CDK (once per account/region)

Go to your AWS account, and copy the account number and region. Then run:

```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### Configure Odoo Credentials

You need to provide the following credentials:

- Odoo URL: The URL of your Odoo instance, without the `https://`. Example: for `https://erp.example.es`, the URL is
  `erp.example.es`.
- Odoo DB: The name of your Odoo database. You can find its name by logging out of Odoo and going to `Manage Databases`.
- Odoo Port: The port of your Odoo instance. Default is 443.
- Odoo Version: The version of your Odoo instance. Default is 16.0.
- Odoo Username: The username of your Odoo account. It is your email address.
- Odoo Password: The password of your Odoo account. Keep it safe.
- Odoo Employee ID: Your employee ID in Odoo. You can find it by navigating to `Employees/your-profile`.
  The url should be `https://erp.example.es/web#id=ODOO_EMPLOYEE_ID&[...]&model=hr.employee.public&view_type=form`.

Then, create `.env.json` file, and input the credentials as follows (keep in mind all values must be strings):

```json
{
  "ODOO_URL": "<your_odoo_url>",
  "ODOO_DB": "<your_db>",
  "ODOO_PORT": "443",
  "ODOO_VERSION": "16.0",
  "ODOO_USERNAME": "<your_username>",
  "ODOO_PASSWORD": "<your_password>",
  "ODOO_EMPLOYEE_ID": "<your_employee_id>"
}
```

## Deployment

```bash
poetry run cdk deploy --require-approval never
```
