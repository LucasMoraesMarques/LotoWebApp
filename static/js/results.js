// Draws Tab

$("#get-results-form input[name=lottery_name]").on("click", function () { // Get current lottery draws numbers
  $.ajax({
    type: "GET",
    url: `get-draws/${this.value}`,
    success: function (response) {
      console.log(response)
      var draws = response["draws"]
      var collections = response["collections"]
      var colSelect = $("#collection-select-draw")
      var drawSelect = $("#draw-select")
      colSelect.empty()
      drawSelect.empty()
      for (draw of draws) {
        drawSelect.append(
          `<option value="${draw.number}">${draw.number}</option>`
        )
      }
      for (collection of collections) {
        colSelect.append(
          `<option value="${collection.id}">${collection.name}</option>`
        )
      }
      if (collections.length == 0){
        $("#get-results-form button[type=submit]").addClass("disabled")
        Toast.fire({
            title: "Crie coleções",
            text: "Não há coleções para essa loteria",
            icon: "warning"
        })
      }
      else{
        $("#get-results-form button[type=submit]").removeClass("disabled")
      }

    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }

  })
})


$("#get-results-form").submit(function (e) { // Submit collection to check in a given draw and receive a file with points by game
  e.preventDefault()
  var serializedData = $(this).serialize()
  console.log(serializedData)
  spinner = createSpinnerLoading("Gerando resultado ...")
  $("#generate-results-btn").hide()
  $("#get-results-form").append(spinner)

  $.ajax({
    type: "POST",
    url: "/create-results-report",
    data: serializedData,
    success: function (response) {
      $(this).trigger('reset')
      console.log(response)
      var draw = response["draw"]
      var filepath = response["filepath"]
      var total_balance = response["total_balance"]
      var result_id = response["result_id"]
      $("#draw-number").html(`Nº ${draw.number} de ${draw.date}`)
      $("#draw-accumulated").html(draw.hasAccumulated ? "Sim" : "Não")
      $("#draw-result").html(`${draw.result.join(separator = "-")}`)
      var currency = { minimumFractionDigits: 2, style: 'currency', currency: 'BRL' }
      $("#draw-prize").html(draw.maxPrize.toLocaleString("pt-br", currency))
      $("#download-result-file").show()
      $("#download-result-file").html(
        `<span>Baixe o resultado gerado com os quantitativos abaixo. Clique no arquivo para baixar.</span>
      <div class="dropdown mx-auto d-inline">
                <a href="javascript:;" class="btn-icon dropdown-toggle" data-bs-toggle="dropdown"
                   id="navbarDropdownMenuLink2">
                  <i class="fa fa-file-text fs-3 mx-3 text-primary"></i>
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink2">
                  <li>
                    <a class="dropdown-item" href="${filepath}" target="_blank">
                      <i class="fa fa-file-export fs-5 mx-2 text-primary"></i>Abrir em nova aba
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="${filepath}" download>
                      <i class="fa fa-file-download fs-5 mx-2 text-primary"></i>Baixar
                    </a>
                  </li>
                </ul>
              </div>`
      )
      $("#get-results-form").append(`<a href="resultados/${result_id}" class="btn btn-secondary mx-2"> Ver página do resultado</a>`)
      $("#n-jogos").html(total_balance["Numero de Jogos"])
      $("#value-paid").html(total_balance["Valor Gasto"].toLocaleString("pt-br", currency))
      $("#prizes-value").html(total_balance["Premiacao"].toLocaleString("pt-br", currency))
      $("#balance").html(total_balance["Saldo"].toLocaleString("pt-br", currency))
      Toast.fire({
    icon: 'success',
    title: "Sucesso",
    text: "Resultado gerado com sucesso!"
})
  $("#spinner").remove()
  $("#generate-results-btn").show()
    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }

  })
})
$(document).ready(function(){
$('.table').DataTable({
    "language": {
      "lengthMenu": "Mostrar _MENU_ jogos por página",
      "zeroRecords": "",
      "info": "Página _PAGE_ de _PAGES_",
      "infoEmpty": "Nenhum jogo encontrado",
      "infoFiltered": "(Filtrados de _MAX_ jogos)",
      "paginate": {
        "previous": "←",
        "next": "→"
      },
      "searchPlaceholder": "Busque jogos por loteria, nome ou status",
      "search": "Filtrar"

    },
    "dom": "fBrtip",
    "buttons": [
            {
            "extend": "collection",
            "text": "Selecionar",
            "autoClose": true,
            "className": "btn btn-primary d-none opacity-0",
            "buttons":[
                {
                    "extend": "selectAll",
                    "text": "Selecionar tudo",
                    "className": "btn btn-secondary px-3 py-2"
                },
                {
                    "extend": "selectNone",
                    "text": "Limpar seleção",
                    "className": "btn btn-secondary px-3 py-2"
                },
            ]
            },
    ],

    "columnDefs": [ {
            "orderable": false,
            "className": 'select-checkbox',
            "targets":   0
        },
         ],
    "select": {
        "style": "multi",
        "selector": "td:first-child",
    },
  });
})