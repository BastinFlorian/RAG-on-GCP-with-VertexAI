terraform {
  backend "gcs" {
    bucket = "<my-tfstate-bucket>"
    prefix = "terraform/tf-boostrap"
  }
}
