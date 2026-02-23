// Configuración (Hardcoded por ahora, idealmente vendría de un config.json generado)
const CONFIG = {
    API_URL: 'https://07wrw4bg9j.execute-api.us-east-1.amazonaws.com',
    CLIENT_ID: '4qa2s8qsqhqbmcu2ska4p88s4d',
    REGION: 'us-east-1'
};

// Estado
let token = localStorage.getItem('id_token') || null;

// Elementos DOM
const loginSection = document.getElementById('login-section');
const registerSection = document.getElementById('register-section');
const verifySection = document.getElementById('verify-section');
const appSection = document.getElementById('app-section');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginMessage = document.getElementById('login-message');
const userDisplay = document.getElementById('user-display');
const itemList = document.getElementById('item-list');

// UI Toggles
function showLogin() {
    loginSection.style.display = 'block';
    registerSection.style.display = 'none';
    verifySection.style.display = 'none';
    appSection.style.display = 'none';
}

function showRegister() {
    loginSection.style.display = 'none';
    registerSection.style.display = 'block';
    verifySection.style.display = 'none';
}

function showVerify(email) {
    loginSection.style.display = 'none';
    registerSection.style.display = 'none';
    verifySection.style.display = 'block';
    document.getElementById('verify-email').value = email;
}

// Inicialización
if (token) {
    showApp();
}

function showApp() {
    loginSection.style.display = 'none';
    registerSection.style.display = 'none';
    verifySection.style.display = 'none';
    appSection.style.display = 'block';
    userDisplay.textContent = `Usuario: ${parseJwt(token).email || 'Conectado'}`;
    loadItems();
}

function logout() {
    token = null;
    localStorage.removeItem('id_token');
    showLogin();
    emailInput.value = '';
    passwordInput.value = '';
    itemList.innerHTML = '';
}

// Auth Functions
async function register() {
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    const messageEl = document.getElementById('register-message');

    if (password !== confirmPassword) {
        messageEl.textContent = 'Las contraseñas no coinciden';
        return;
    }

    try {
        const response = await fetch(`https://cognito-idp.${CONFIG.REGION}.amazonaws.com/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target': 'AWSCognitoIdentityProviderService.SignUp'
            },
            body: JSON.stringify({
                ClientId: CONFIG.CLIENT_ID,
                Username: email,
                Password: password,
                UserAttributes: [{ Name: 'email', Value: email }]
            })
        });

        const data = await response.json();

        if (response.ok) {
            showVerify(email);
        } else {
            messageEl.textContent = data.message || 'Error en registro';
        }
    } catch (error) {
        console.error(error);
        messageEl.textContent = 'Error de red';
    }
}

async function verifyCode() {
    const email = document.getElementById('verify-email').value;
    const code = document.getElementById('verify-code').value;
    const messageEl = document.getElementById('verify-message');

    try {
        const response = await fetch(`https://cognito-idp.${CONFIG.REGION}.amazonaws.com/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target': 'AWSCognitoIdentityProviderService.ConfirmSignUp'
            },
            body: JSON.stringify({
                ClientId: CONFIG.CLIENT_ID,
                Username: email,
                ConfirmationCode: code
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Cuenta verificada. Ahora puedes iniciar sesión.');
            showLogin();
            document.getElementById('email').value = email;
        } else {
            messageEl.textContent = data.message || 'Error en verificación';
        }
    } catch (error) {
        console.error(error);
        messageEl.textContent = 'Error de red';
    }
}

async function login() {
    const email = emailInput.value;
    const password = passwordInput.value;
    loginMessage.textContent = 'Autenticando...';

    try {
        const target = 'AWSCognitoIdentityProviderService.InitiateAuth';
        const response = await fetch(`https://cognito-idp.${CONFIG.REGION}.amazonaws.com/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target': target
            },
            body: JSON.stringify({
                ClientId: CONFIG.CLIENT_ID,
                AuthFlow: 'USER_PASSWORD_AUTH',
                AuthParameters: {
                    USERNAME: email,
                    PASSWORD: password
                }
            })
        });

        const data = await response.json();

        if (response.ok) {
            token = data.AuthenticationResult.IdToken; // Usamos IdToken
            localStorage.setItem('id_token', token);
            loginMessage.textContent = '';
            showApp();
        } else {
            loginMessage.textContent = data.message || 'Error en login';
        }
    } catch (error) {
        console.error(error);
        loginMessage.textContent = 'Error de red';
    }
}

async function loadItems() {
    itemList.innerHTML = '<li>Cargando...</li>';
    try {
        const response = await fetch(`${CONFIG.API_URL}/items`, {
            headers: {
                Authorization: token
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        const items = await response.json();
        renderItems(items);
    } catch (error) {
        itemList.innerHTML = '<li>Error al cargar ítems</li>';
    }
}


let isEditing = false;

async function handleSave() {
    if (isEditing) {
        updateItem();
    } else {
        createItem();
    }
}

function startEdit(id, name, category, price) {
    isEditing = true;
    document.getElementById('form-title').textContent = 'Editar Ítem';
    document.getElementById('save-btn').textContent = 'Guardar Cambios';
    document.getElementById('cancel-btn').style.display = 'inline-block';

    // We store the ID somewhere to be used for the PUT request
    document.getElementById('item-name').dataset.editingId = id;
    document.getElementById('item-name').value = name;
    document.getElementById('item-category').value = category;
    document.getElementById('item-price').value = price;
}

function cancelEdit() {
    isEditing = false;
    document.getElementById('form-title').textContent = 'Nuevo Ítem';
    document.getElementById('save-btn').textContent = 'Crear';
    document.getElementById('cancel-btn').style.display = 'none';

    document.getElementById('item-name').value = '';
    document.getElementById('item-category').value = '';
    document.getElementById('item-price').value = '';
}

async function updateItem() {
    const id = document.getElementById('item-name').dataset.editingId;
    const name = document.getElementById('item-name').value;
    const category = document.getElementById('item-category').value;
    const price = document.getElementById('item-price').value;

    if (!name || !category || !price) {
        alert('Rellena nombre, categoría y precio');
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_URL}/items/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                category: category,
                price: parseFloat(price)
            })
        });

        if (response.ok) {
            cancelEdit();
            loadItems();
        } else {
            alert('Error al actualizar ítem');
        }
    } catch (error) {
        console.error(error);
        alert('Error de red');
    }
}

async function deleteItem(id) {
    if (!confirm(`¿Seguro que quieres borrar el ítem ${id}?`)) return;

    try {
        const response = await fetch(`${CONFIG.API_URL}/items/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': token
            }
        });

        if (response.ok) {
            loadItems();
            if (isEditing && document.getElementById('item-name').dataset.editingId === id) {
                cancelEdit();
            }
        } else {
            alert('Error al borrar ítem');
        }
    } catch (error) {
        console.error(error);
        alert('Error de red');
    }
}

function renderItems(items) {
    itemList.innerHTML = '';
    if (items.length === 0) {
        itemList.innerHTML = '<li>No hay ítems. ¡Crea uno!</li>';
        return;
    }
    items.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span><strong>${item.name}</strong> - ${item.category || 'Sin categoría'} ($${item.price}) <small>(ID: ${item.itemId})</small></span>
            <div>
                <button onclick="startEdit('${item.itemId}', '${item.name}', '${item.category || ''}', ${item.price})" style="background-color: #ffc107; color: black; margin-right: 5px;">Editar</button>
                <button onclick="deleteItem('${item.itemId}')" style="background-color: #dc3545;">Borrar</button>
            </div>
        `;
        itemList.appendChild(li);
    });
}

// Keep createItem but remove the duplicate declaration of renderItems and others if they exist in the replaced block.
// To be safe, I will implement createItem here as well to match the previous structure and just update the UI reset part.

async function createItem() {
    const name = document.getElementById('item-name').value;
    const category = document.getElementById('item-category').value;
    const price = document.getElementById('item-price').value;

    if (!name || !category || !price) {
        alert('Rellena todos los campos');
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_URL}/items`, {
            method: 'POST',
            headers: {
                'Authorization': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                category: category,
                price: parseFloat(price)
            })
        });

        if (response.ok) {
            cancelEdit(); // Limpia el formulario
            loadItems();
        } else {
            const data = await response.json();
            alert('Error al crear ítem: ' + (data.error || 'Desconocido'));
        }
    } catch (error) {
        console.error(error);
        alert('Error de red');
    }
}


// Utilidad para decodificar JWT (sin validar firma, solo para sacar datos)
function parseJwt(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}
