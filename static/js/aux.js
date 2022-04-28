// Aux. Functions
months = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro"
]

messagesTitles = {
  "error": "Erro!",
  "success": "Sucesso!",
  "info": "Atenção!",
  "warning": "Atenção!"
}

function createSpinnerLoading(message) {
  return `<div class="d-flex flex-row" id="spinner">
    <div class="spinner-border text-primary mx-3" role="status">
    </div>
    <p>${message}</p>
  </div>
  `
}

function showAlertMessage(message, type = "info") {
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
  timer: 3000,
  timerProgressBar: true
})

const SwalModal = Swal.mixin({
  showDenyButton: true,
  confirmButtonText: "SIM",
  denyButtonText: "NÃO",
  confirmButtonColor: "green",
  customClass: {
  actions: 'my-actions',
  confirmButton: 'order-1',
  denyButton: 'order-2',
}
})

function fireToast(message, title, iconType) {
  return Toast.fire({
    icon: iconType,
    title: title,
    text: message,
  })
}

function fireModal(message, title, iconType) {
  return SwalModal.fire({
    icon: iconType,
    title: title,
    text: message,
  })
}


async function fireMessagesToasts() {
  messages = $("#messages li")
  for (message of messages) {
    messageTag = message.classList[0]
    messageTitle = messagesTitles[messageTag]
    await fireToast($(message).text(), messageTitle, messageTag)
  }
}

$("[name=select-all]").click(function(){
  var table = $(this).parents("table").first()
    table = table.DataTable()
    if($(this).prop("checked")){
  table.rows().select()
}
    else {
  table.rows().deselect()
}
})