# Cloud function service account
resource "google_service_account" "function_service_account" {
  account_id   = var.functions_service_account_name
  display_name = "Service Account for cloud functions"
}

module "functions_member_roles" {
  source                  = "terraform-google-modules/iam/google//modules/member_iam"
  service_account_address = google_service_account.function_service_account.email
  prefix                  = "serviceAccount"
  project_id              = var.project_id
  project_roles           = var.cloudfunctions_sa_roles
}

# Create zip archive with cloud functions code
data "archive_file" "cloud_functions" {
  type             = "zip"
  source_dir       = var.funtions_source_dir
  output_file_mode = "0666"
  output_path      = var.functions_output_zip_path
}


# Upload zip code of function in bucket for the function
resource "google_storage_bucket_object" "rag_functions" {
  name   = local.functions_gcs_zip_object
  bucket = google_storage_bucket.rag_bucket.name
  source = data.archive_file.cloud_functions.output_path
}


# Function to process data and save result in csv file on bucket
resource "google_cloudfunctions2_function" "update_active_pages" {
  name        = var.cloud_functions_name
  location    = var.location
  description = "Function to update and process active pages"

  build_config {
    runtime     = "python310"
    entry_point = "main"
    environment_variables = {
      GOOGLE_FUNCTION_SOURCE = var.functions_main_file
    }
    source {
      storage_source {
        bucket = google_storage_bucket.rag_bucket.name
        object = google_storage_bucket_object.rag_functions.name
      }
    }
  }

  event_trigger {
    event_type            = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic          = google_pubsub_topic.trigger_update_pages.id
    service_account_email = google_service_account.function_service_account.email
    trigger_region        = var.location
    retry_policy          = "RETRY_POLICY_UNSPECIFIED"
  }

  service_config {
    service_account_email = google_service_account.function_service_account.email
    max_instance_count    = 1
    available_memory      = "512M"
    timeout_seconds       = 60
    ingress_settings      = "ALLOW_INTERNAL_ONLY"

    environment_variables = {
      for env_var in local.env_vars : env_var.name => env_var.value
    }

    dynamic "secret_environment_variables" {
      for_each = var.env_secrets
      content {
        project_id = var.project_id
        key        = secret_environment_variables.value.env_name
        secret     = secret_environment_variables.value.secret_name
        version    = secret_environment_variables.value.secret_version
      }
    }
  }

}


# Pubsub topic to tigger function
resource "google_pubsub_topic" "trigger_update_pages" {
  name                       = var.cloud_functions_topic_name
  message_retention_duration = "604800s"
  project                    = var.project_id
}


# Cron job to schedule Pubsub
resource "google_cloud_scheduler_job" "invoke_update_pages_function" {
  name        = var.cloud_functions_scheduler_name
  description = "Schedule the Pubsub trigger for cloud function"
  schedule    = var.scheduler
  project     = google_cloudfunctions2_function.update_active_pages.project
  region      = google_cloudfunctions2_function.update_active_pages.location

  pubsub_target {
    topic_name = google_pubsub_topic.trigger_update_pages.id
    data       = base64encode("Trigger to update pages and ai index")
  }
}
