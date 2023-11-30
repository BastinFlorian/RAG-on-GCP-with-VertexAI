resource "google_bigquery_dataset" "genai_bq_dataset" {
  dataset_id  = "genai_dataset"
  project     = var.project_id
  description = "Dataset for GenAI"
  location    = "EU"

  access {
    role          = "OWNER"
    user_by_email = google_service_account.cloud_run_sa.email
  }
  access {
    role          = "WRITER"
    user_by_email = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  }
}

resource "google_bigquery_table" "genai_bq_table" {
  dataset_id          = google_bigquery_dataset.genai_bq_dataset.dataset_id
  table_id            = "genai-feedback"
  project             = var.project_id
  deletion_protection = false # set to "true" in production

  schema = <<EOF
[
  {
    "name": "id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "UUID"
  },
  {
    "name": "rating",
    "type": "INT64",
    "mode": "NULLABLE",
    "description": "User rating"
  },
  {
    "name": "feedback",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Feedback provided by the user"
  },
  {
    "name": "question",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Question asked by the used"
  },
  {
    "name": "response",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Response predicted by the model"
  },
  {
    "name": "sources",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "URLs used to answer the question"
  },
  {
    "name": "runtime",
    "type": "FLOAT64",
    "mode": "NULLABLE",
    "description": "Time taken to answer the question"
  },
  {
    "name": "datetime",
    "type": "DATETIME",
    "mode": "NULLABLE",
    "description": "Feedback datetime"
  }
]
EOF
}