## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | 5.7.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_cloud_run_sa_iam"></a> [cloud\_run\_sa\_iam](#module\_cloud\_run\_sa\_iam) | git@github.com:terraform-google-modules/terraform-google-iam.git//modules/member_iam | n/a |
| <a name="module_lb-http"></a> [lb-http](#module\_lb-http) | GoogleCloudPlatform/lb-http/google//modules/serverless_negs | n/a |

## Resources

| Name | Type |
|------|------|
| [google_artifact_registry_repository.rag-repo](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/artifact_registry_repository) | resource |
| [google_bigquery_dataset.genai_bq_dataset](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset) | resource |
| [google_bigquery_table.genai_bq_table](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_table) | resource |
| [google_cloud_run_service.main](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_service) | resource |
| [google_cloud_run_service_iam_member.authorize](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_service_iam_member) | resource |
| [google_compute_global_address.default](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_global_address) | resource |
| [google_compute_region_network_endpoint_group.serverless_neg](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_region_network_endpoint_group) | resource |
| [google_iap_client.iap_client](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iap_client) | resource |
| [google_iap_web_backend_service_iam_policy.policy](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iap_web_backend_service_iam_policy) | resource |
| [google_pubsub_schema.gen_ai_pubsub_schema](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_schema) | resource |
| [google_pubsub_subscription.gen_ai_pubsub_subscription](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_subscription) | resource |
| [google_pubsub_topic.gen_ai_pubsub_topic](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_topic) | resource |
| [google_service_account.cloud_run_sa](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account) | resource |
| [google_storage_bucket.rag_bucket](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket) | resource |
| [google_storage_bucket_object.data](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket_object) | resource |
| [google_vertex_ai_index.index](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vertex_ai_index) | resource |
| [google_vertex_ai_index_endpoint.index_endpoint](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vertex_ai_index_endpoint) | resource |
| [google_iam_policy.iap](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/iam_policy) | data source |
| [google_project.project](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/project) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cloudrun_sa_roles"></a> [cloudrun\_sa\_roles](#input\_cloudrun\_sa\_roles) | Roles to apply to cloudrun sa | `list(string)` | `[]` | no |
| <a name="input_container_command"></a> [container\_command](#input\_container\_command) | Leave blank to use the ENTRYPOINT command defined in the container image, include these only if image entrypoint should be overwritten | `list(string)` | `[]` | no |
| <a name="input_container_concurrency"></a> [container\_concurrency](#input\_container\_concurrency) | Concurrent request limits to the service | `number` | `null` | no |
| <a name="input_enable_iap"></a> [enable\_iap](#input\_enable\_iap) | If True it will create OAuth2 client\_id/secret and enable IAP on the loadbalancer | `bool` | `false` | no |
| <a name="input_enable_lb"></a> [enable\_lb](#input\_enable\_lb) | If yes it will create GCP Loadbalancer in front of the Cloud RUN | `bool` | `true` | no |
| <a name="input_env_secret_vars"></a> [env\_secret\_vars](#input\_env\_secret\_vars) | Secret Environment variables (Secret Manager) | <pre>list(object({<br>    name = string<br>    value_from = set(object({<br>      secret_key_ref = map(string)<br>    }))<br>  }))</pre> | `[]` | no |
| <a name="input_env_vars"></a> [env\_vars](#input\_env\_vars) | Environment variables (cleartext) | <pre>list(object({<br>    value = string<br>    name  = string<br>  }))</pre> | `[]` | no |
| <a name="input_iap_http_accessor"></a> [iap\_http\_accessor](#input\_iap\_http\_accessor) | IAP members allowed to access (asign roles/iap.httpsResourceAccessor) | `list(string)` | <pre>[<br>  "allAuthenticatedUsers"<br>]</pre> | no |
| <a name="input_image"></a> [image](#input\_image) | GCR hosted image URL to deploy | `string` | n/a | yes |
| <a name="input_lb_domain"></a> [lb\_domain](#input\_lb\_domain) | loadbalancer domain names | `string` | `"rag.example.com"` | no |
| <a name="input_lb_ip_address_name"></a> [lb\_ip\_address\_name](#input\_lb\_ip\_address\_name) | Existing IPv4 address to use (the actual IP address value) | `string` | `"rag-api"` | no |
| <a name="input_lb_name"></a> [lb\_name](#input\_lb\_name) | Cloud run loadbalancer name | `string` | `"rag-lb"` | no |
| <a name="input_limits"></a> [limits](#input\_limits) | Resource limits to the container | `map(string)` | <pre>{<br>  "cpu": "1",<br>  "memory": "256Mi"<br>}</pre> | no |
| <a name="input_location"></a> [location](#input\_location) | Cloud Run service deployment location | `string` | `"europe-west1"` | no |
| <a name="input_members"></a> [members](#input\_members) | Users/SAs to be given invoker access to the service | `list(string)` | `[]` | no |
| <a name="input_oauth_brand_name"></a> [oauth\_brand\_name](#input\_oauth\_brand\_name) | Identifier of the brand to which this client is attached to. The format is projects/{project\_number}/brands/{brand\_id}/identityAwareProxyClients/{client\_id}. | `string` | `null` | no |
| <a name="input_oauth_client_display_name"></a> [oauth\_client\_display\_name](#input\_oauth\_client\_display\_name) | Display name given to the OAuth client. | `string` | `null` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | The project ID to deploy to | `string` | n/a | yes |
| <a name="input_rag_bucket_name"></a> [rag\_bucket\_name](#input\_rag\_bucket\_name) | RAG GCS bucket | `string` | n/a | yes |
| <a name="input_run_service_account_display_name"></a> [run\_service\_account\_display\_name](#input\_run\_service\_account\_display\_name) | Service Account display name | `string` | `"Cloud RUN Service Account"` | no |
| <a name="input_run_service_account_id"></a> [run\_service\_account\_id](#input\_run\_service\_account\_id) | Service Account ID | `string` | `"rag-run-sa"` | no |
| <a name="input_service_annotations"></a> [service\_annotations](#input\_service\_annotations) | Annotations to the service. Acceptable values all, internal, internal-and-cloud-load-balancing | `map(string)` | <pre>{<br>  "run.googleapis.com/ingress": "all"<br>}</pre> | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | The name of the Cloud Run service to create | `string` | n/a | yes |
| <a name="input_template_annotations"></a> [template\_annotations](#input\_template\_annotations) | Annotations to the container metadata including VPC Connector and SQL. | `map(string)` | <pre>{<br>  "autoscaling.knative.dev/maxScale": 2,<br>  "autoscaling.knative.dev/minScale": 1,<br>  "generated-by": "terraform",<br>  "run.googleapis.com/client-name": "terraform"<br>}</pre> | no |
| <a name="input_timeout_seconds"></a> [timeout\_seconds](#input\_timeout\_seconds) | Timeout for each request | `number` | `120` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_external_ip"></a> [external\_ip](#output\_external\_ip) | LB external IP |
| <a name="output_index_endpoint_id"></a> [index\_endpoint\_id](#output\_index\_endpoint\_id) | n/a |
| <a name="output_index_id"></a> [index\_id](#output\_index\_id) | n/a |
| <a name="output_service_account_email"></a> [service\_account\_email](#output\_service\_account\_email) | cloud run service account email |
| <a name="output_service_url"></a> [service\_url](#output\_service\_url) | The URL on which the deployed service is available |
