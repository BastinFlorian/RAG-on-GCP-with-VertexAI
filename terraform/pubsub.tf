# Create a PubSub subscription connected to BigQuery

resource "google_pubsub_schema" "gen_ai_pubsub_schema" {
  name       = "genai-pubsub-schema"
  project    = var.project_id
  type       = "AVRO"
  definition = <<EOF
  {
    "type": "record",
    "name": "Avro",
    "fields": [
        {
        "name": "id",
        "type": "string"
        },
        {
        "name": "rating",
        "type": "int",
        "default": null
        },
        {
        "name": "feedback",
        "type": "string",
        "default": null
        },
        {
        "name": "question",
        "type": "string",
        "default": null
        },
        {
        "name": "response",
        "type": "string",
        "default": null
        },
        {
        "name": "sources",
        "type": "string",
        "default": null
        },
        {
        "name": "runtime",
        "type": "float",
        "default": null
        },
        {
        "name": "datetime",
        "type": "string",
        "default": "0"
        }
    ]
    }
EOF
}

resource "google_pubsub_topic" "gen_ai_pubsub_topic" {
  name       = "gen-ai-pubsub-topic"
  project    = var.project_id
  depends_on = [google_pubsub_schema.gen_ai_pubsub_schema]

  schema_settings {
    schema   = google_pubsub_schema.gen_ai_pubsub_schema.id
    encoding = "JSON"
  }

}

resource "google_pubsub_subscription" "gen_ai_pubsub_subscription" {
  name    = "gen-ai-pubsub-subscription"
  topic   = google_pubsub_topic.gen_ai_pubsub_topic.name
  project = var.project_id

  bigquery_config {
    table            = "${google_bigquery_table.genai_bq_table.project}.${google_bigquery_table.genai_bq_table.dataset_id}.${google_bigquery_table.genai_bq_table.table_id}"
    use_topic_schema = true
  }

}
