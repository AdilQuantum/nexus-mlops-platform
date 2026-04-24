variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "nexus-mlops"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "nat_ami" {
  type        = string
  description = "NAT instance AMI for us-east-1"
  default     = "ami-0a6b2839d44d781b2"
}

variable "db_username" {
  type      = string
  sensitive = true
  default   = "mlflow"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "changeme123!"
}