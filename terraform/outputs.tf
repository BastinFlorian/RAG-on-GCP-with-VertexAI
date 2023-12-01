output "index_endpoint_id" {
  value       = google_vertex_ai_index_endpoint.index_endpoint.name
  description = "Vertex AI endpoint ID"
}

output "index_id" {
  value       = google_vertex_ai_index.index.name
  description = "Vertex AI index ID"
}

output "service_url" {
  value       = google_cloud_run_service.main.status[0].url
  description = "The URL on which the deployed service is available"
}

output "external_ip" {
  description = "LB external IP"
  value       = var.enable_lb ? module.lb-http.*.external_ip : null
}