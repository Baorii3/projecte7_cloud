resource "aws_cognito_user_pool" "main" {
  name = var.user_pool_name

  # Permitir registro de usuarios (Self-registration)
  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  # Login con email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Política de contraseñas simple (mínimo 6 caracteres)
  password_policy {
    minimum_length    = 6
    require_lowercase = false
    require_numbers   = false
    require_symbols   = false
    require_uppercase = false
  }

  mfa_configuration = "OFF"

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "Código de Verificación"
    email_message        = "Tu código de verificación es {####}"
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name = var.client_name

  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret     = false
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH", 
    "ALLOW_REFRESH_TOKEN_AUTH", 
    "ALLOW_USER_SRP_AUTH"
  ]
}
