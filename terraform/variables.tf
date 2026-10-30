variable "project_id" {
  description = "GCP project hosting Apigee X, Model Armor, and Vertex AI."
  type        = string
}

variable "region" {
  description = "Region for Model Armor templates and other regional resources."
  type        = string
  default     = "us-central1"
}

variable "apigee_analytics_region" {
  description = "Apigee analytics region (required when creating a new Apigee org)."
  type        = string
  default     = "us-central1"
}

variable "create_apigee_org" {
  description = <<-EOT
    Whether this stack should provision a brand-new Apigee X organization.
    Most teams already have one; leave this false and set
    apigee_environment_name to an existing environment in that case.
  EOT
  type    = bool
  default = false
}

variable "apigee_environment_name" {
  description = "Apigee environment the proxy and shared flow are deployed to."
  type        = string
  default     = "eval"
}

variable "model_armor_template_id" {
  description = "ID for the Model Armor template guarding agent input/output."
  type        = string
  default     = "agent-io-template"
}
