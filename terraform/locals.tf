locals {
  env_vars = concat(var.env_vars, [
    {
      name  = "INDEX_ENDPOINT_ID"
      value = google_vertex_ai_index_endpoint.index_endpoint.name
    },
    {
      name  = "INDEX_ID"
      value = google_vertex_ai_index.index.name
    },
    {
      name  = "PROJECT_ID"
      value = var.project_id
    },
    {
      name  = "BUCKET_NAME"
      value = google_storage_bucket.rag_bucket.name
    },
    {
      name  = "REGION"
      value = var.location
    },
    {
      name  = "FIRESTORE_DATABASE_NAME"
      value = google_firestore_database.database.name
    },
  ])

  functions_gcs_zip_object = "cloud_functions/rag.${data.archive_file.cloud_functions.output_md5}.zip" #  append MD5 checksum of the content of zip to trigger update
}
