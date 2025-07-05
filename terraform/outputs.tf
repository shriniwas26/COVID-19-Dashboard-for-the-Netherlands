output "elastic_beanstalk_environment_url" {
  description = "URL of the Elastic Beanstalk environment"
  value       = aws_elastic_beanstalk_environment.env.endpoint_url
}

output "elastic_beanstalk_environment_name" {
  description = "Name of the Elastic Beanstalk environment"
  value       = aws_elastic_beanstalk_environment.env.name
}

output "elastic_beanstalk_application_name" {
  description = "Name of the Elastic Beanstalk application"
  value       = aws_elastic_beanstalk_application.app.name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for application versions"
  value       = aws_s3_bucket.eb_app_versions.bucket
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.eb_sg.id
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.eb_logs.name
}


