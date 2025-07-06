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

variable "domain_name" {
  description = "Custom domain name for the application"
  type        = string
  default     = "covid-dashboard-nl.ss2201.nl"
}

variable "route53_zone_id" {
  description = "Route 53 hosted zone ID"
  type        = string
  default     = "YOUR_HOSTED_ZONE_ID"
}

variable "enable_https" {
  description = "Enable HTTPS with custom domain"
  type        = bool
  default     = true
}

variable "netlify_verification_txt" {
  description = "TXT record value for Netlify domain verification"
  type        = string
  default     = ""
}
