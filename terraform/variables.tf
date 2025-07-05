variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "dashboard-nl-ss2201"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}
