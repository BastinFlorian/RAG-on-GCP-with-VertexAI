# Create Cloud run service account
resource "google_service_account" "cloud_run_sa" {
  project      = var.project_id
  account_id   = var.run_service_account_id
  display_name = var.run_service_account_display_name
}

module "cloud_run_sa_iam" {
  source = "git@github.com:terraform-google-modules/terraform-google-iam.git//modules/member_iam"

  project_id              = var.project_id
  service_account_address = google_service_account.cloud_run_sa.email
  project_roles           = var.cloudrun_sa_roles
}


resource "google_cloud_run_service_iam_member" "authorize" {
  count = var.enable_lb ? 1 : 0

  location = google_cloud_run_service.main.location
  project  = google_cloud_run_service.main.project
  service  = google_cloud_run_service.main.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-iap.iam.gserviceaccount.com"
}

resource "google_cloud_run_service" "main" {
  name     = var.service_name
  location = var.location
  project  = var.project_id

  metadata {
    annotations = var.service_annotations
  }

  template {
    spec {
      containers {
        image   = var.image
        command = var.container_command

        resources {
          limits = var.limits
        }

        dynamic "env" {
          for_each = local.env_vars
          content {
            name  = env.value["name"]
            value = env.value["value"]
          }
        }

        dynamic "env" {
          for_each = var.env_secrets
          content {
            name = env.value["env_name"]
            value_from {
              secret_key_ref {
                name = env.value["secret_name"]
                key  = env.value["secret_version"]
              }
            }
          }
        }

      }                                                 // container
      container_concurrency = var.container_concurrency # maximum allowed concurrent requests 0,1,2-N
      timeout_seconds       = var.timeout_seconds       # max time instance is allowed to respond to a request
      service_account_name  = google_service_account.cloud_run_sa.email

    }
    metadata {
      annotations = var.template_annotations
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }

  lifecycle {
    ignore_changes = [
      traffic,
      template[0].metadata[0].labels["run.googleapis.com/startupProbeType"],
      template[0].spec[0].containers[0].image,
      metadata[0].annotations["client.knative.dev/user-image"],
      metadata[0].annotations["run.googleapis.com/client-name"],
      metadata[0].annotations["run.googleapis.com/client-version"],
      metadata[0].annotations["run.googleapis.com/operation-id"],
      template[0].metadata[0].annotations["client.knative.dev/user-image"],
      template[0].metadata[0].annotations["run.googleapis.com/client-name"],
      template[0].metadata[0].annotations["run.googleapis.com/client-version"],
    ]
  }
}



####  Loadbalancer Config

resource "google_compute_global_address" "default" {
  count      = var.enable_lb ? 1 : 0
  project    = var.project_id
  name       = var.lb_ip_address_name
  ip_version = "IPV4"
}

module "lb-http" {
  source = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
  count  = var.enable_lb ? 1 : 0

  name                            = var.lb_name
  project                         = var.project_id
  ssl                             = true
  managed_ssl_certificate_domains = [var.lb_domain]
  https_redirect                  = true
  address                         = join("", google_compute_global_address.default.*.address)
  create_address                  = false
  backends = {
    default = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.serverless_neg[0].id
        }
      ]
      enable_cdn              = false
      security_policy         = null
      custom_request_headers  = null
      custom_response_headers = null
      protocol                = null
      port_name               = null
      compression_mode        = null
      iap_config = {
        enable               = var.enable_iap
        oauth2_client_id     = var.enable_iap ? join("", google_iap_client.iap_client.*.client_id) : ""
        oauth2_client_secret = var.enable_iap ? join("", google_iap_client.iap_client.*.secret) : ""
      }
      log_config = {
        enable      = false
        sample_rate = null
      }
    }
  }
}
resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  count = var.enable_lb ? 1 : 0

  name                  = "neg-${google_cloud_run_service.main.name}"
  network_endpoint_type = "SERVERLESS"
  project               = var.project_id
  region                = var.location
  cloud_run {
    service = google_cloud_run_service.main.name
  }
}

#### Create OAuth2 credentials for IAP
resource "google_iap_client" "iap_client" {
  count = var.enable_iap ? 1 : 0

  display_name = var.oauth_client_display_name
  brand        = "projects/${data.google_project.project.number}/brands/${data.google_project.project.number}"
}

resource "google_iap_web_backend_service_iam_policy" "policy" {
  count = var.enable_iap ? 1 : 0

  project             = var.project_id
  web_backend_service = join("", module.lb-http.*.backend_services.default.name)
  policy_data         = data.google_iam_policy.iap.policy_data
}