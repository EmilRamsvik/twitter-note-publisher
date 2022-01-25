
provider "google" {
  project = "twitter-notes-338310"
  region  = "europe-west2"
  credentials = "${file("${var.path}/credentials.json")}"
}

# 
resource "google_storage_bucket" "bucket" {
  name="bucket-twitter-notes"
}

# This is the data that contains the code that the cloud function will run.
# Thse source_dir is the directory that contains the python code. 
data "archive_file" "source" {
  type   = "zip"
  source_dir = "${path.root}/../twitter"
  output_path = "${path.root}/../generated/twitter.zip"
}

# Storage bucket that contains the source code (?) the name gets a unique id
# for the data.md5 hash. This is because terraform wont pick up changes in code
# unless it has a new name. 
resource "google_storage_bucket_object" "archive" {
  name = "${data.archive_file.source.output_md5}.zip"
  bucket = google_storage_bucket.bucket.name
  source = "${path.root}/../generated/twitter.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "function-test"
  runtime     = "python38"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "hello_world"
  environment_variables = {
AIRTABLE_API_KEY="${var.AIRTABLE_API_KEY}"
TWITTER_ACCESS_TOKEN_SECRET="${var.TWITTER_ACCESS_TOKEN_SECRET}"
TWITTER_ACCESS_TOKEN="${var.TWITTER_ACCESS_TOKEN}"
TWITTER_CONSUMER_SECRET="${var.TWITTER_CONSUMER_SECRET}"
TWITTER_CONSUMER_KEY="${var.TWITTER_CONSUMER_KEY}"
  }
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}


# '# The cloud function needs a service account that is credentialed to run it. 
# resource "google_service_account" "service_account" {
#   account_id = "cloud-function-invoker"
#   display_name = "twitter-bot-proj-booknotes-poster"
# }

# resource "google_project_iam_member" "invoker" {
#   project = google_cloudfunctions_function.function.project

#   role = "roles/cloudfunctions.invoker"
#   member = "serviceAccount:${google_service_account.service_account.email}"
# } 

# resource "google_cloud_scheduler_job" "job" {
#   name = "twitter-bot-proj-booknotes-poster"
#   description = "Schedule the ${google_cloudfunctions_function.function.name} function to run every 5 minutes"
#   schedule = "every 5 minutes"
#   time_zone = "Europe/London"
#   http_target {
#     http_method = "GET"
#     uri         = google_cloudfunctions_function.function.https_trigger_url

#     oidc_token {
#       service_account_email = google_service_account.service_account.email
#     }
#   }
#   }'