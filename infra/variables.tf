variable "path" {
  default = "/Users/emilseverinramsvik/Documents/twitter-note-publisher/infra/"
  description = "Path to the project terrafrom directory"
}

variable "AIRTABLE_API_KEY" {
  sensitive = true
  default = "API key to the airtable database"
}
variable "TWITTER_ACCESS_TOKEN_SECRET" {
  sensitive = true
  description = "From Twitter Developer account"
}
variable "TWITTER_ACCESS_TOKEN" {
  sensitive = true
  description = "From Twitter Developer account"
}
variable "TWITTER_CONSUMER_SECRET" {
  sensitive = true
  description = "From Twitter Developer account"
}
variable "TWITTER_CONSUMER_KEY" {
  sensitive = true
  description = "From Twitter Developer account"
}
# variable "GOOGLE_APPLICAION_CREDENTIALS" {
#   sensitive = true
#   description = "JSON credentials for the service account"
# }