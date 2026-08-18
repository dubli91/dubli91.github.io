# Tech Stack

> Listed in order of proficiency.

---


## Primary Languages & Frameworks

| Technology | One-line comment |
| --- | --- |
| Python | Backend server development with Python 3.11–14 and the FastAPI + UV combo |
| Java | Development and maintenance of legacy backend servers at the Java 8–11 level |
| C / C++ | Data structures / algorithm problem-solving level |


## Frameworks & Backend Technologies

| Technology | One-line comment |
| --- | --- |
| FastAPI | First to introduce FastAPI + UV within my department and shared best practices; REST API development; service deployment via AWS Lambda and k8s |
| Spring Boot | REST API development with TDD, introduced Spring REST Docs, image builds with the jib plugin |


## Infrastructure / DevOps

### IaaS
I've mostly worked on AWS, and recently adopted GCP as well, so I'm building up GCP operations experience too.

| Technology | One-line comment |
| --- | --- |
| AWS Lambda | Running FastAPI services via the [aws-lambda-adapter](https://github.com/aws/aws-lambda-web-adapter) |
| AWS EKS | Availability and version management for the home-appliance traffic collection and processing (Smarthome) cluster / using Karpenter |
| GCP GKE | Infrastructure operations for AI servers for home appliances / using Keda |
| AWS EC2 | Operating legacy Spring Boot-based backend server code |

### Monitoring / CICD
| Technology | One-line comment |
| --- | --- |
| Github Action | Built verification and deployment pipelines for both EC2-based and K8S-based services |
| LGT stack | Grafana + Prometheus + Loki + Open Telemetry + Tempo + FluentBit on GCP |
| Argo CD / Rollout | Set up Argo CD deployments on GCP / Canary deployments with Argo Rollouts |


## Databases

| Technology | One-line comment |
| --- | --- |
| Redis / Valkey | Using AWS Elasticache for storing auth data and caching |
| NoSQL | AWS DynamoDB and MongoDB Atlas, accessed via PynamoDB |
| Mysql | Using AuroraDB, accessed via jdbc |
