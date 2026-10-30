# Apigee X organization/environment wiring.
#
# This is intentionally minimal: most teams run this against an Apigee X
# org that already exists. Set create_apigee_org = true only for a
# from-scratch demo project, and expect to also need an instance +
# environment group + attachment, which varies enough by network setup
# (PSC vs. non-PSC, existing VPC, etc.) that it's left out of this
# scaffold on purpose — follow the codelab linked in the README for that
# part, or adapt google_apigee_instance / google_apigee_envgroup here.

resource "google_apigee_organization" "org" {
  count = var.create_apigee_org ? 1 : 0

  provider                             = google-beta
  project_id                           = var.project_id
  analytics_region                     = var.apigee_analytics_region
  disable_vpc_peering                  = true
  depends_on                           = [google_project_service.required]
}

resource "google_apigee_environment" "env" {
  count = var.create_apigee_org ? 1 : 0

  provider     = google-beta
  org_id       = google_apigee_organization.org[0].id
  name         = var.apigee_environment_name
  display_name = var.apigee_environment_name
}

# KVM holding the Model Armor template coordinates the shared flow reads
# at runtime (apigee/sharedflows/model-armor-sf). Works against either a
# pre-existing or newly created environment.
#
# NOTE: google_apigee_keyvaluemap(_entry) resources and their exact field
# names have changed across terraform-provider-google releases. Verify
# against the provider version you pin in versions.tf before applying;
# if your pinned version lacks them, create the KVM with `apigeecli kvms`
# instead and skip this block.
resource "google_apigee_keyvaluemap" "model_armor_config" {
  provider = google-beta
  org_id   = var.project_id
  name     = "model-armor-config"
}

resource "google_apigee_keyvaluemap_entry" "project_id" {
  provider     = google-beta
  env_keyvaluemap_id = google_apigee_keyvaluemap.model_armor_config.id
  name         = "gcp.project_id"
  value        = var.project_id
}

resource "google_apigee_keyvaluemap_entry" "location" {
  provider     = google-beta
  env_keyvaluemap_id = google_apigee_keyvaluemap.model_armor_config.id
  name         = "gcp.location"
  value        = var.region
}

resource "google_apigee_keyvaluemap_entry" "template_id" {
  provider     = google-beta
  env_keyvaluemap_id = google_apigee_keyvaluemap.model_armor_config.id
  name         = "modelarmor.template_id"
  value        = var.model_armor_template_id
}
