resource "google_artifact_registry_repository" "rag" {
  location      = var.location
  repository_id = var.artifactregistry_name
  description   = "RAG Docker repository"
  format        = "DOCKER"
}
