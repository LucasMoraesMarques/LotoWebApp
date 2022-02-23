// Aux. Functions

function createSpinnerLoading(message){
  return `<div class="d-flex flex-row" id="spinner">
    <div class="spinner-border text-primary mx-3" role="status">
    </div>
    <p>${message}</p>
  </div>
  `
}

function showAlertMessage(message, type="info"){
  $("#messages span.alert-text").text(message)
  $("#messages").removeClass()
  $("#messages").addClass(`alert alert-${type} alert-dismissible fade show float-right`)
  $("#messages").show()
}

const Toast = Swal.mixin({
    toast: true,
    position: 'top-right',
    iconColor: 'white',
    customClass: {
      popup: 'colored-toast'
    },
    showConfirmButton: false,
    timer: 1500,
    timerProgressBar: true
  })