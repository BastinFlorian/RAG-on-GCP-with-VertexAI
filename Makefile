include src/.env


# Tests
test-confluence:
	poetry run pytest tests/test_confluence.py

test:
	poetry run pytest


# Local development
init-data:
	poetry run python -m upload_data.data_init

update-data:
	poetry run python -m upload_data.data_update

open-notebook:
	poetry run ipython kernel install --user --name=rag-evaluation
	poetry run jupyter lab

docker-build:
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	docker buildx build --platform linux/amd64 --push -t europe-west1-docker.pkg.dev/$(PROJECT_ID)/rag-api/gen-ai:latest .

demo:
	docker build -t gcp-rag-streamlit:latest .
	docker run -p 8501:8501 gcp-rag-streamlit


# Service account
create-sa-with-roles: create-sa create-roles add-user-to-impersonate-sa enable-gcp-services allow-user-to-get-access-token-from-sa

create-sa:
	gcloud iam service-accounts create gen-ai --display-name="rag-gen-ai-sa"

create-roles:
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/aiplatform.user"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/datastore.user"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/iam.serviceAccountUser"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/run.admin"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/storage.admin"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/storage.objectAdmin"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/storage.objectUser"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/bigquery.dataOwner"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/pubsub.editor"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/iam.securityReviewer"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/iam.securityAdmin"


add-user-to-impersonate-sa:
	gcloud iam service-accounts add-iam-policy-binding \
		gen-ai@$(PROJECT_ID).iam.gserviceaccount.com\
		--member="user:$(USER_EMAIL)" \
		--role="roles/iam.serviceAccountUser"


enable-gcp-services:
	gcloud services enable cloudresourcemanager.googleapis.com
	gcloud services enable serviceusage.googleapis.com
	gcloud services enable cloudbuild.googleapis.com
	gcloud services enable secretmanager.googleapis.com
	gcloud services enable run.googleapis.com
	gcloud services enable aiplatform.googleapis.com
	gcloud services enable firebaserules.googleapis.com
	gcloud services enable firestore.googleapis.com
	gcloud services enable ml.googleapis.com
	gcloud services enable artifactregistry.googleapis.com
	gcloud services enable bigquery.googleapis.com
	gcloud services enable bigquerymigration.googleapis.com
	gcloud services enable bigquerystorage.googleapis.com


allow-user-to-get-access-token-from-sa:
	gcloud projects add-iam-policy-binding $(PROJECT_NUMBER) \
		--member="user:$(USER_EMAIL)" --role=roles/iam.workloadIdentityUser \
		--condition=None


# Impersonation
impersonate-service-account:
	gcloud auth application-default login --impersonate-service-account gen-ai@$(PROJECT_ID).iam.gserviceaccount.com


# Docker
create-artefact-registry:
	gcloud artifacts repositories create gen-ai \
    --repository-format=docker \
    --location=europe-west1 \
    --description="Generative Ai Rag" \
    --async


# Helpers
list-sa-roles:
	gcloud projects get-iam-policy $(PROJECT_ID) \
	--flatten="bindings[].members" \
	--format='table(bindings.role)' \
	--filter="bindings.members:gen-ai@$(PROJECT_ID).iam.gserviceaccount.com"

describe-index:
	gcloud ai indexes describe $(INDEX_ID) --project=$(PROJECT_ID) --region=$(REGION)


# Vertex AI Vector Search
# Create
create-index:
	gcloud ai indexes create \
	--metadata-file="./vertex_search_index_metadata.json" \
	--display-name=rag-index \
	--project=$(PROJECT_ID) \
	--region=$(REGION)

create-index-endpoint:
	gcloud ai index-endpoints create \
	--display-name=rag-endpoint  \
	--project=$(PROJECT_ID)  \
	--region=$(REGION)

deploy-vertex-endpoint:
	gcloud ai index-endpoints deploy-index $(INDEX_ENDPOINT_ID) \
	--index=$(INDEX_ID) \
	--deployed-index-id=$(DEPLOYED_INDEX_ID) \
	--display-name=ragendpoint \
	--region $(REGION)

# Update
update-index:
	gcloud ai indexes update $(INDEX_ID) \
  	--metadata-file=$(INDEX_METADATA_JSON_PATH) \
  	--region=$(REGION)


# Delete
delete-vector-search: undeploy-index delete-index_endpoint delete_index

undeploy-index:
	gcloud ai index-endpoints undeploy-index $(INDEX_ENDPOINT_ID) --project=$(PROJECT_ID) \
	--region=europe-west1 --deployed-index-id=$(DEPLOYED_INDEX_ID)

delete-index-endpoint:
	gcloud ai index-endpoints delete $(INDEX_ENDPOINT_ID) \
  	--region=europe-west1

delete-index:
	gcloud ai indexes delete $(INDEX_ID) \
	--project=$(PROJECT_ID) \
	--region=$(REGION)
