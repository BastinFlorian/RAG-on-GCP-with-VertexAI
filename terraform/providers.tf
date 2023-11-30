terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.location
  zone    = "${var.location}-b"
}