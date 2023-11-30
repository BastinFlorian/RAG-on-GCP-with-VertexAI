resource "google_storage_bucket" "rag_bucket" {
  name          = var.rag_bucket_name
  project       = var.project_id
  location      = var.location
  force_destroy = true
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
}

#empty file to init google_vertex_ai_index
resource "google_storage_bucket_object" "data" {
  name    = "contents/example.json"
  bucket  = google_storage_bucket.rag_bucket.name
  content = " "
}


resource "google_vertex_ai_index" "index" {
  region       = var.location
  project      = var.project_id
  display_name = "rag-index"
  description  = "index for test"
  metadata {
    contents_delta_uri = "gs://${google_storage_bucket.rag_bucket.name}/contents/"
    config {
      dimensions                  = 768
      approximate_neighbors_count = 150
      shard_size                  = "SHARD_SIZE_MEDIUM"
      distance_measure_type       = "DOT_PRODUCT_DISTANCE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 5000
          leaf_nodes_to_search_percent = 3
        }
      }
    }
  }
  index_update_method = "BATCH_UPDATE"

}

# INDEX ENDPONT
resource "google_vertex_ai_index_endpoint" "index_endpoint" {
  display_name = "rag-endpoint"
  project      = var.project_id
  description  = "Endpoint for the Retrieval Augmentation demo"
  region       = var.location
}