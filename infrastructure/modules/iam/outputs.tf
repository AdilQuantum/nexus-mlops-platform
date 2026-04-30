output "eks_cluster_role_arn" {
  value = aws_iam_role.eks_cluster.arn
}

output "eks_node_role_arn" {
  value = aws_iam_role.eks_node.arn
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "Paste this into GitHub Secrets as AWS_ROLE_ARN"
}