terraform {
  backend "gcs" {
    bucket = "<my-tfstate-bucket>" # <my-tfstate-bucket>
    prefix = "terraform/tf-rag-infra"
  }
}
