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
  default = "staging"
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