import boto3
import argparse
import sys
import os

# Configuración 
USER_POOL_ID = 'us-east-1_vLUxayPoB'
CLIENT_ID = '4qa2s8qsqhqbmcu2ska4p88s4d'
REGION = 'us-east-1'

client = boto3.client('cognito-idp', region_name=REGION)

def signup(email, password):
    try:
        response = client.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )
        print(f"Usuario {email} creado exitosamente.")
        print(f"Siguiente paso: Ejecuta 'python3 scripts/auth_manager.py confirm {email}' para activarlo.")
    except client.exceptions.UsernameExistsException:
        print(f"El usuario {email} ya existe.")
    except Exception as e:
        print(f"Error al registrarse: {e}")

def confirm_user(email):
    """Admin confirma al usuario (salta verificación por email para pruebas)"""
    try:
        client.admin_confirm_sign_up(
            UserPoolId=USER_POOL_ID,
            Username=email
        )
        print(f"Usuario {email} confirmado exitosamente por Admin.")
    except Exception as e:
        print(f"Error al confirmar usuario: {e}")

def login(email, password):
    try:
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Necesitamos el ID Token (no Access Token) para el Authorizer de API Gateway
        token = response['AuthenticationResult']['IdToken']
        
        print("\n" + "="*50)
        print("¡INICIO DE SESIÓN EXITOSO!")
        print("="*50)
        print(f"\nID_TOKEN:\n{token}\n")
        print("="*50)
        print("\nComando para probar tu API:")
        print(f'curl -H "Authorization: {token}" https://07wrw4bg9j.execute-api.us-east-1.amazonaws.com/items')
        return token
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Asistente de Autenticación Cognito')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Signup
    signup_parser = subparsers.add_parser('signup', help='Crear un nuevo usuario')
    signup_parser.add_argument('email', help='Correo del usuario')
    signup_parser.add_argument('password', help='Contraseña del usuario')

    # Confirm (Admin)
    confirm_parser = subparsers.add_parser('confirm', help='Confirmar usuario (Bypass Admin)')
    confirm_parser.add_argument('email', help='Correo del usuario')

    # Login
    login_parser = subparsers.add_parser('login', help='Iniciar sesión y obtener Token')
    login_parser.add_argument('email', help='Correo del usuario')
    login_parser.add_argument('password', help='Contraseña del usuario')

    args = parser.parse_args()

    if args.command == 'signup':
        signup(args.email, args.password)
    elif args.command == 'confirm':
        confirm_user(args.email)
    elif args.command == 'login':
        login(args.email, args.password)
