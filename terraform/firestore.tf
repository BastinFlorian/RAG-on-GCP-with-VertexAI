resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = var.firestore_database_name
  location_id = var.firestore_region
  type        = "FIRESTORE_NATIVE"
}
