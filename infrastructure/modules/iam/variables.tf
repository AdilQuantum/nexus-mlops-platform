variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "github_repo" {
  type        = string
  description = "GitHub repo in owner/name format, e.g. AdilQuantum/nexus-mlops-platform"
}