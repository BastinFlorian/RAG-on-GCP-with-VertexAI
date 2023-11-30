data "google_project" "project" {
  project_id = var.project_id
}

data "google_iam_policy" "iap" {
  binding {
    role    = "roles/iap.httpsResourceAccessor"
    members = var.iap_http_accessor
  }
}