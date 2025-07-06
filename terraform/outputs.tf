output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "public_url" {
  description = "Public URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "https_url" {
  description = "HTTPS URL to access the application"
  value       = var.enable_https ? (var.domain_name != "" ? "https://${var.domain_name}" : aws_cloudfront_distribution.main[0].domain_name) : "https://${aws_lb.main.dns_name}"
}

output "cloudfront_url" {
  description = "CloudFront HTTPS URL (when no custom domain)"
  value       = var.enable_https && var.domain_name == "" ? "https://${aws_cloudfront_distribution.main[0].domain_name}" : null
}

output "custom_domain_url" {
  description = "Custom domain URL (if HTTPS is enabled)"
  value       = var.enable_https ? "https://${var.domain_name}" : null
}

output "target_group_arn" {
  description = "The ARN of the target group"
  value       = aws_lb_target_group.app.arn
}
