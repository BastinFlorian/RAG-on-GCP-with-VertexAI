resource "google_service_account" "service_account" {
  account_id   = var.service_account_name
  display_name = "Service Account for Terraform"
}

module "member_roles" {
  source                  = "terraform-google-modules/iam/google//modules/member_iam"
  service_account_address = google_service_account.service_account.email
  prefix                  = "serviceAccount"
  project_id              = var.project_id
  project_roles = [
    "roles/run.admin",
    "roles/storage.admin",
    "roles/iam.serviceAccountCreator",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/resourcemanager.projectIamAdmin",
    "roles/bigquery.admin",
    "roles/pubsub.editor",
    "roles/aiplatform.admin",
    "roles/artifactregistry.admin",
    "roles/compute.admin",
    "roles/oauthconfig.editor",
    "roles/iap.admin",
    "roles/datastore.owner",
    "roles/cloudfunctions.admin",
    "roles/cloudscheduler.admin",
  ]
}

module "project-services" {
  source     = "terraform-google-modules/project-factory/google//modules/project_services"
  project_id = var.project_id
  activate_apis = [
    "compute.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "pubsub.googleapis.com",
    "aiplatform.googleapis.com",
    "firestore.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
  ]
}
