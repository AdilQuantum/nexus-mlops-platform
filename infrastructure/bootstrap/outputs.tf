output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "Add this to GitHub Secrets as AWS_ROLE_ARN"
}
