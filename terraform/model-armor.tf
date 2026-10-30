# Model Armor template applied by BOTH the agent (direct API calls, see
# agent/model_armor_client.py) and the Apigee shared flow (see
# apigee/sharedflows/model-armor-sf). Using the same template id in both
# places keeps the two layers' policies in sync; point them at different
# templates if you want the gateway check to be stricter/looser than the
# agent's own check.
#
# NOTE: Model Armor's Terraform resource surface is new and may still be
# changing. Verify the resource name/fields against the current
# hashicorp/google provider docs before applying; if it's not available
# yet in your pinned provider version, create the template with
# `gcloud model-armor templates create` instead and reference the same
# template id in agent/.env and the model-armor-config KVM above.

resource "google_model_armor_template" "agent_io" {
  provider     = google-beta
  project      = var.project_id
  location     = var.region
  template_id  = var.model_armor_template_id

  filter_config {
    rai_settings {
      rai_filters {
        filter_type      = "HATE_SPEECH"
        confidence_level = "MEDIUM_AND_ABOVE"
      }
      rai_filters {
        filter_type      = "SEXUALLY_EXPLICIT"
        confidence_level = "MEDIUM_AND_ABOVE"
      }
      rai_filters {
        filter_type      = "HARASSMENT"
        confidence_level = "MEDIUM_AND_ABOVE"
      }
      rai_filters {
        filter_type      = "DANGEROUS"
        confidence_level = "MEDIUM_AND_ABOVE"
      }
    }
    pi_and_jailbreak_filter_settings {
      filter_enforcement = "ENABLED"
      confidence_level    = "MEDIUM_AND_ABOVE"
    }
    sdp_settings {
      basic_config {
        filter_enforcement = "ENABLED"
      }
    }
  }

  depends_on = [google_project_service.required]
}
