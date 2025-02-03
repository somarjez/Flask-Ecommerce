$('.plus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('pid').toString()
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            cart_id: id
        },
        
        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total

        }
    })
})


$('.minus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('pid').toString()
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            cart_id: id
        },
        
        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total

        }
    })
})

$('.remove-cart').click(function(){
    
    var id = $(this).attr('pid').toString()

    var to_remove = this.parentNode.parentNode.parentNode.parentNode

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },

        success: function(data){
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total
            to_remove.remove()
        }
    })



})
$('.remove-wishlist').click(function() {
    var id = $(this).attr('pid').toString();  // Get the wishlist item ID
    var to_remove = this.closest('.row');  // Get the closest parent row to remove

    $.ajax({
        type: 'GET',
        url: '/remove-wishlist',  // Endpoint for removing the wishlist item
        data: {
            wishlist_id: id  // Send the wishlist ID to the server
        },
        success: function(data) {
            // alert(data.message);  // Show success message
            to_remove.remove();  // Remove the item from the DOM
        },
        error: function(xhr, status, error) {
            console.error(xhr.responseText);  // Log any errors
            alert('An error occurred while removing the item from the wishlist.');
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Highlight table row on hover
    const rows = document.querySelectorAll(".table-hover tbody tr");
    rows.forEach(row => {
        row.addEventListener("mouseover", () => {
            row.style.backgroundColor = "#d3d3d3";
        });
        row.addEventListener("mouseout", () => {
            row.style.backgroundColor = "";
        });
    });

    document.addEventListener("DOMContentLoaded", function() {
        const confirmLinks = document.querySelectorAll(".box-link");
        confirmLinks.forEach(link => {
            link.addEventListener("click", (event) => {
                const confirmAction = confirm("Are you sure you want to proceed?");
                if (!confirmAction) {
                    event.preventDefault();
                }
            });
        });
    });
});

// scripts.js (make sure to link this in your base.html)
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const tableRows = document.querySelectorAll('.table tbody tr');

    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        tableRows.forEach(row => {
            const cells = row.getElementsByTagName('td');
            let match = false;
            for (let cell of cells) {
                if (cell.textContent.toLowerCase().includes(filter)) {
                    match = true;
                    break;
                }
            }
            row.style.display = match ? '' : 'none';
        });
    });
});

// scripts.js

// Function to filter table rows based on search input
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const tableRows = document.querySelectorAll(".table tbody tr");

    searchInput.addEventListener("keyup", function () {
        const filter = searchInput.value.toLowerCase();

        tableRows.forEach(row => {
            const cells = row.getElementsByTagName("td");
            let rowVisible = false;

            for (let i = 0; i < cells.length; i++) {
                if (cells[i].innerText.toLowerCase().includes(filter)) {
                    rowVisible = true;
                    break;
                }
            }

            row.style.display = rowVisible ? "" : "none";
        });
    });
});

setTimeout(function() {
    const alert = document.querySelector('.alert');
    if (alert) {
        alert.classList.remove('show');
    }
}, 3000);
  // Save current scroll position and URL before the reload
  window.addEventListener('beforeunload', function() {
      localStorage.setItem('scrollPosition', window.scrollY);
      localStorage.setItem('pageUrl', window.location.href);
  });