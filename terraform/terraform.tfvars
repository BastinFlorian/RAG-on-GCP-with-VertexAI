
### ------------- Mandatory to change ------------- ###

project_id              = "test-project"     # <my-project-id>
rag_bucket_name         = "rag-gcp-bucket"    # ex: rag_bucket_name (bucket name must be globally unique)
location                = "europe-west1"
firestore_database_name = "rag-firestore-db"
# Warning: choose a different bucket than the one used for terraform state

# Set to false if you want to allow all users to access the app
# Set to true if you want to restrict access to the app to a specific user.
# If true you need to have a domain name and the oauth client id
enable_iap = false
enable_lb  = false

# Replace with the pushed GCR image url
image = "europe-west1-docker.pkg.dev/my-project-id/rag-api/gen-ai"


### ------------- Mandatory to change if enable_iap = true and enable_lb = true ------------- ###



# If enable_iap = true and enable_lb = true
# Set to "internal-and-cloud-load-balancing"
# Else, set to "all"
service_annotations = {
  "run.googleapis.com/ingress" = "all"
}

# If enable_iap = true and enable_lb = true
# Update the domain name
lb_domain = "11-222-333-444.sslip.io"




### ------------- Create the secrets in the secret manager ------------- ###




env_vars = [
  {
    name  = "DEPLOYED_INDEX_ID"
    value = "ragdeployedindex"
  }

]

env_secrets = [
  {
    env_name       = "CONFLUENCE_PRIVATE_API_KEY"
    secret_name    = "CONFLUENCE_PRIVATE_API_KEY"
    secret_version = "latest"
  },
  {
    env_name       = "CONFLUENCE_URL"
    secret_name    = "CONFLUENCE_URL"
    secret_version = "latest"
  },
  {
    env_name       = "CONFLUENCE_EMAIL_ADRESS"
    secret_name    = "CONFLUENCE_EMAIL_ADRESS"
    secret_version = "latest"
  },
  {
    env_name       = "CONFLUENCE_SPACE_NAMES"
    secret_name    = "CONFLUENCE_SPACE_NAMES"
    secret_version = "latest"
  }
]
