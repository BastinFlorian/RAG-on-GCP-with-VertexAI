resource "google_service_account_iam_binding" "service-account-iam" {
  service_account_id = google_service_account.service_account.id
  role               = "roles/iam.serviceAccountTokenCreator"
  members = [
    "user:${var.gcp_account_email}",
  ]
}
