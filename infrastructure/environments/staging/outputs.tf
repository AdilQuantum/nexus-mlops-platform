output "github_actions_role_arn" {
  value       = module.iam.github_actions_role_arn
  description = "Add this to GitHub Secrets as AWS_ROLE_ARN"
}
