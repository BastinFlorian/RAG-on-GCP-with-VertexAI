variable "project_id" {
  type    = string
  default = "my-project"
}

variable "location" {
  type    = string
  default = "europe-west1"
}

variable "artifactregistry_name" {
  type    = string
  default = "rag-api"
}

variable "gcp_account_email" {
  type = string
}

variable "service_account_name" {
  type    = string
  default = "terraform-sa"
}
