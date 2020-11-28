function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function promptMessage(message, classes) {
    var outer = document.createElement("div");
    outer.className += 'prompt-box';

    var inner = document.createElement("div");
    inner.innerHTML = message;
    inner.className = classes;
    
    outer.appendChild(inner);
    document.body.appendChild(outer);
    
    setTimeout(function(){outer.remove();}, 3000);
}

function showLoginModal() {
    $('#loginModal').modal('show');
    showLoginForm();
}

function clearLoginInput() {
    document.getElementById("login-modal-content").querySelectorAll("input").forEach(function(element) {
        if (element.name == "mobile") {
            element.value = "+60";
        }
        else {
            element.value = "";
        }
    })
}

function showRegisterForm() {
    $("#modalLabel").html('REGISTER');
    $("#loginForm").hide();
    $("#registerForm").show();
    $("#login-error").html('');
    $("#login-error").hide();
    clearLoginInput();
}

function showLoginForm() {
    $("#modalLabel").html("LOGIN");
    $("#registerForm").hide();
    $("#loginForm").show();
    $("#login-error").html('');
    $("#login-error").hide();
    clearLoginInput();
}

function login() {
    var form = document.getElementById("loginForm");
    formData = new FormData(form);

    fetch('/accounts/login/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData,
    })
    .then(response => response.json())
    .then(result => {
        if (result.status) {
            window.location.reload();
        }
        else {
            document.getElementById("login-error").innerHTML = result.message;
            $('#login-error').show();
        }
    });

}

function register() {
    var form = document.getElementById("registerForm");
    formData = new FormData(form);

    fetch('/accounts/register/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.status) {
            $('#loginModal').modal('hide');
            promptMessage("Account created successfully", "alert alert-success");
            setTimeout(function(){window.location.reload();}, 3000);
        }
        else {
            document.getElementById("login-error").innerHTML = result.message;
        }
    });

}

document.querySelectorAll('.input-number').forEach(function(element) { 
    element.addEventListener("keypress", function(event) {
        if (isNaN(event.key)) {
            event.preventDefault();
        } else if (event.key == " ") {
            event.preventDefault();
        }

    });

    element.addEventListener("keyup", function(event) {
        // use parseInt to remove the extra 0 in front of the input quantity
        var quantity = parseInt(this.value);

        if (quantity > 999) {
            // set maximum to 999
            this.value = 999;
        } 
        
        else if (quantity < 1 || isNaN(quantity)) {
            // set minimum to 1
            this.value = 1;
        }

        else {
            this.value = quantity;
        }
    });
});

$('.quantity-right-plus').click(function(e){
    
    // Stop acting like a button
    e.preventDefault();
    // Get the field name
    var quantity = parseInt(this.parentNode.children[1].value);
    
    // If is not undefined
        if(quantity<999){
            this.parentNode.children[1].value = quantity + 1;
        }
        // Increment
    
});

$('.quantity-left-minus').click(function(e){
    // Stop acting like a button
    e.preventDefault();
    // Get the field name
    var quantity = parseInt(this.parentNode.children[1].value);
    
    // If is not undefined
    
        // Increment
        if(quantity>1){
            this.parentNode.children[1].value = quantity - 1;
        }
});

function addItem(id) {
    var formData = new FormData(document.querySelector("#product-form"));
    // Find section text from server
    fetch(`/product/${id}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.status) {
            document.querySelector('#itemNum').innerHTML = result.quantity__sum;

            $('#exampleModal').modal('show');
            if (result.selection) {
                document.querySelector("#selection").innerHTML = result.selection;
            }
            document.querySelector('#priceModal').innerHTML = `RM${result.total_price}`;
            document.querySelector('#quantityModal').innerHTML = document.querySelector(".input-number").value;
        }

        else {
            showLoginModal();
            $('#modalLabel').html('Please login to continue');
        }
    });
};

document.querySelectorAll('.remove').forEach(function(element){
    element.addEventListener('click', function(){
        document.getElementById('confirm-remove').dataset.id = element.dataset.id;
    })
})

if (document.querySelectorAll('.remove').length != 0) {
    var confirm_remove = document.getElementById('confirm-remove');

    confirm_remove.addEventListener('click', function() {
        fetch(`/remove/${confirm_remove.dataset.id}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
        })
        .then(response => response.json())
        .then(result => {
            document.getElementById(`remove-cart-${confirm_remove.dataset.id}`).parentNode.parentNode.parentNode.parentNode.remove();
            document.querySelector('#itemNum').innerHTML = result.quantity__sum;
            if (result.quantity__sum != 0) {
                document.querySelector('#subtotal').innerHTML = result.subtotal;
                document.querySelector('#total').innerHTML = result.subtotal;
            }
            else {
                document.querySelector('#subtotal').innerHTML = "0.00";
                document.querySelector('#total').innerHTML = "0.00";
                var div = document. createElement("div");
                div.innerHTML = "Your cart has no item.";
                div.className = "text-center my-5";
                document.getElementById("cart-items").replaceChild(div, document.getElementById("cart-items").children[0]);
                document.querySelector('.place-order').disabled = true;
            }
            
        })

    })
}

function updateProfile() {
    var form = document.getElementById("profile-info");
    var inputs = form.querySelectorAll('input');

    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].value == "") {
            promptMessage("Please do not leave any info blank", "alert alert-danger");
            return;
        }
    }

    formData = new FormData(form);

    fetch('/accounts/profile/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.status) {
            document.getElementById('nav-first-name').innerHTML = result.name;
            promptMessage(result.message, "alert alert-success");
        }
        else {
            promptMessage(result.message, "alert alert-danger");
            document.getElementById('email').value = result.email;
            document.getElementById('mobile').value = result.mobile;
        }
    });

}

function changePassword() {
    var form = document.getElementById("profile-password");
    var inputs = form.querySelectorAll('input');

    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].value == "") {
            promptMessage("Please do not leave any blank", "alert alert-danger");
            return;
        }
    }

    formData = new FormData(form);

    fetch('/accounts/change_password/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.status) {
            promptMessage(result.message, "alert alert-success");
            document.getElementById("profile-password").querySelectorAll("input").forEach(function(element) {
                element.value = "";
            })
        }
        else {
            promptMessage(result.message, "alert alert-danger");
            document.getElementById("profile-password").querySelectorAll("input").forEach(function(element) {
                element.value = "";
            })
        }
    });

}

if (document.querySelector('.update-cart')) {
    document.querySelector('.update-cart').addEventListener("click", function(){
        var icon = document.createElement("i");
        icon.className = "fas fa-spinner fa-spin";
        this.replaceChild(icon, this.childNodes[0]);
        var formData = new FormData();
        document.querySelectorAll(".input-number").forEach(function(element){
            formData.append(element.dataset.id, element.value);
        })
        fetch('/cart/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            var textnode = document.createTextNode("UPDATE CART");
            document.querySelector('.update-cart').replaceChild(textnode, document.querySelector('.update-cart').childNodes[0]);
            document.querySelector('#itemNum').innerHTML = result.quantity__sum;
            document.querySelector('#subtotal').innerHTML = result.subtotal;
            document.querySelector('#total').innerHTML = result.subtotal;
        });

    })
}

if (document.querySelector('.place-order')) {
    var cart_item_number = document.querySelector('#itemNum').innerHTML;

    if (cart_item_number == "0") {
        document.querySelector('.place-order').disabled = true;
    }

    else {
        document.querySelector('.place-order').addEventListener('click', function() {
            fetch('/order/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(result => {
                if (result.url) {
                    window.location.href = result.url;
                }
                else {
                    promptMessage("Your cart has no item, please refresh your browser.", "alert alert-danger")
                }
            });    
        })
    }
}

document.querySelectorAll('.receive').forEach(function(element){
    element.addEventListener('click', function(){
        var formData = new FormData();
        formData.append('topup_id', element.dataset.id);
        fetch('/accounts/topup-manage/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            element.parentNode.parentNode.remove();
            var table = document.querySelector('#table-body');
            if (table.childElementCount == 0) {
                var div = document.createElement("div");
                div.innerHTML = "No active top up request currently.";
                div.className = "text-center my-5";
                document.getElementById("section-content").replaceChild(div, document.getElementById("section-content").children[0]);
            }
        })
    })
})

document.querySelectorAll('.cancel-topup').forEach(function(element){
    element.addEventListener('click', function(){
        document.getElementById('confirm-remove').dataset.id = element.dataset.id;
    })
})

if (document.querySelectorAll('.cancel-topup').length != 0) {
    var x = document.getElementById('confirm-remove');
    x.addEventListener('click', function(){
        var formData = new FormData();
        formData.append("topup_id", x.dataset.id);
        fetch('/accounts/cancel/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            document.getElementById(`cancel-topup-${x.dataset.id}`).parentNode.parentNode.remove();
        })
    })
}

function pay(id) {
    fetch(`/order/${id}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
    })
    .then(response => response.json())
    .then(result => {
        window.location.reload();
    })
}

document.querySelectorAll('.cancel-order').forEach(function(element){
    element.addEventListener('click', function(){
        document.getElementById('order-message').innerHTML = element.dataset.id;
        document.getElementById('confirm-remove').dataset.id = element.dataset.id;
    })
})

if (document.querySelectorAll('.cancel-order').length != 0) {
    var x = document.getElementById('confirm-remove');
    x.addEventListener('click', function(){
        var formData = new FormData();
        formData.append("order_id", x.dataset.id);
        fetch('/cancel/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            document.getElementById(`cancel-order-${x.dataset.id}`).parentElement.parentElement.parentElement.remove();
            var div_pending = document.getElementById("order-pending-payment");
            if (div_pending.childElementCount == 1) {
                var para = document.createElement("p");
                para.innerHTML = "You have no order pending for payment.";
                para.className = "text-center";
                div_pending.appendChild(para);
            }
        })
    })
}