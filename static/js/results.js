function handleDrawsSelect() { // Get current lottery draws numbers
  $.ajax({
    type: "GET",
    url: `get-draws/${this.value}`,
    success: function (response) {
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
      if (collections.length == 0) {
        $("#get-results-form button[type=submit]").addClass("disabled")
        fireToast("Não há coleções para essa loteria", "Crie coleções", "warning")
      }
      else {
        $("#get-results-form button[type=submit]").removeClass("disabled")
      }
    },
    error: function (response) {
      fireToast("Desculpe, ocorreu um erro inesperado. Tente novamente!", "Erro!", "error")
    }
  })
}

function handleResultsGeneration(e) { // Submit collection to check in a given draw and receive a file with points by game
  e.preventDefault()
  var serializedData = $(this).serialize()
  spinner = createSpinnerLoading("Gerando resultado ...")
  $("#generate-results-btn").hide()
  $("#get-results-form").append(spinner)

  $.ajax({
    type: "POST",
    url: "/create-results-report",
    data: serializedData,
    success: function (response) {
      $(this).trigger('reset')
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
      $("#download-result-file ul a").attr("href", filepath)
      $("#see-result-page-btn").show()
      $("#see-result-page-btn").attr("href", `resultados/${result_id}`)
      $("#n-jogos").html(total_balance["Numero de Jogos"])
      $("#value-paid").html(total_balance["Valor Gasto"].toLocaleString("pt-br", currency))
      $("#prizes-value").html(total_balance["Premiacao"].toLocaleString("pt-br", currency))
      $("#balance").html(total_balance["Saldo"].toLocaleString("pt-br", currency))
      fireToast("Resultado gerado com sucesso!", "Sucesso", 'success')
      $("#spinner").remove()
      $("#generate-results-btn").show()
    },
    error: function (response) {
      fireToast(response["responseJSON"]["message"], "Erro!", 'error')
      $("#spinner").remove()
      $("#generate-results-btn").show()
    }
  })
}


function setDataTables() {
  $('.table').DataTable({
    "language": {
      "lengthMenu": "Mostrar _MENU_ resultados por página",
      "zeroRecords": "",
      "info": "Página _PAGE_ de _PAGES_",
      "infoEmpty": "Nenhum resultado encontrado",
      "infoFiltered": "(Filtrados de _MAX_ resultados)",
      "paginate": {
        "previous": "←",
        "next": "→"
      },
      "searchPlaceholder": "Filtre por loteria, coleção ou concurso",
      "search": "Filtrar"

    },
    "dom": "fBlrtip",
    "buttons": [
      {
        "extend": "collection",
        "text": "Selecionar",
        "autoClose": true,
        "className": "btn btn-primary d-none opacity-0",
        "buttons": [
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

    "columnDefs": [{
      "orderable": false,
      "className": 'select-checkbox',
      "targets": 0
    },
    ],
    "select": {
      "style": "multi",
      "selector": "td:first-child",
    },
  });
  $("#results-table_filter input").css("width", "250px")
  $("#results-table_filter").addClass("mb-2")
}

function handleSendResults() {
  var send_by = this.id
  fireModal(`Você realmente deseja enviar os resultados selecionados por ${send_by}?`, "Tem certeza ?", "warning")
    .then((answer) => {
      if (answer.isConfirmed) {
        var table = $("#results-table").DataTable()
        var rows = table.rows({ "selected": true })
        var form = $("#send-results-form")
        if (rows[0].length != 0) {
          for (row of rows[0]) {
            var tr = table.row(row).node()
            var input = $(tr).find("td:first-child input")
            form.append(input)
          }
          form.append(`<input name="method" value="${send_by}" type="hidden">`)
          form.submit()
        }
        else {
          fireToast("Nenhum resultado foi selecionado para envio. Clique nos botões na primeira coluna para selecionar", "Atenção", "warning")
        }
      }

    })
}

function handleDeleteResults() {
  fireModal(`Você realmente deseja DELETAR os resultados selecionados?`,
    "Tem certeza ?", "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var table = $("#results-table").DataTable()
      var rows = table.rows({ "selected": true })
      var form = $("#action-results")
      for (row of rows[0]) {
        var tr = table.row(row).node()
        var input = $(tr).find("td:first-child input")
        form.append(input)
      }
      form.submit()
    }
  })
}

function handleExportResults() {
  fireModal(`Você realmente deseja EXPORTAR os resultados selecionados?`,
    "Tem certeza ?", "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var table = $("#results-table").DataTable()
      var rows = table.rows({ "selected": true })
      var form = $("#export-results-form")
      var lotteries = []
      for (row of rows[0]) {
        var tr = table.row(row).node()
        var input = $(tr).find("td:first-child input").clone()
        var lottery = $(tr).find("p:hidden").text()
        if (!lotteries.includes(lottery)) {
          lotteries.push(lottery)
        }
        form.append(input)
      }
      form.append(`<input type="hidden" name="file-type" value="${this.id}">`)
      if (lotteries.length > 1) {
        fireToast("Selecione somente resultados de uma única modalidade da loteria e exporte por loteria.", "Atenção", "warning")
      }
      else {
        form.submit()
      }
      form.find("input").remove("[name=results]")
      form.find("input").remove("[name=file-type]")
      table.rows().deselect()
    }
  })
}


function showCheckboxes() {
  var checkboxes = $(this).parent().find(".checkBoxes");
  if (show) {
    checkboxes.css("display", "block")
    show = false;
  } else {
    checkboxes.css("display", "none")
    show = true;
  }
}

function handleExportResultGames() {
  fireModal(`Você realmente deseja EXPORTAR os jogos selecionados?`,
    "Tem certeza ?", "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var tables = $(".results-table")
      var form = $("#export-results-reports-games")
      var total = 0
      for (let tb of tables) {
        var table = $(`#${tb.id}`).DataTable()
        var rows = table.rows({ "selected": true })
        for (row of rows[0]) {
          var tr = table.row(row).node()
          var input = $(tr).find("td:first-child input").clone()
          form.append(input)
          total += 1
        }
        table.rows().deselect()
      }

      form.append(`<input type="hidden" name="file-type" value="${this.id}">`)
      if (total == 0) {
        fireToast("Selecione algum jogo para exportar!", "Atenção", "warning")
      }
      else {
        form.submit()
      }
      form.find("input").remove("[name=games]")
      form.find("input").remove("[name=file-type]")

    }
  })

}

function handleCreateGamesetFromSelected() {
  SwalModal
  SwalModal.fire({
    title: 'Criar Conjunto',
    html: `<input type="text" id="gameset-name" class="swal2-input" placeholder="Nome do Conjunto" required>
    <div class="d-flex align-items-center justify-content-center"><span>Ativo?</span>
    <input type="checkbox" id="is-active" class="swal2-input my-auto" placeholder="Ativo?">
    </div>`,
    denyButtonText: "Cancelar",
    confirmButtonText: 'Criar',
    preConfirm: () => {
      const gameSetName = Swal.getPopup().querySelector('#gameset-name').value
      const isActive = Swal.getPopup().querySelector('#is-active').checked
      if(gameSetName.length == 0){
        Swal.showValidationMessage(`Escolha um nome válido`)
      }
      return { gameSetName: gameSetName, isActive: Boolean(isActive) ? 1 : 0}
    }
  }).then((result) => {
    if (result.isConfirmed) {
      var form = $("#create-game-set-form")
      form.append(`<input type="hidden" name="gameset-name" value=${result.value.gameSetName}>`)
      form.append(`<input type="hidden" name="is-active" value=${result.value.isActive}>`)
      var tables = $(".results-table")
      var total = 0
      for (let tb of tables) {
        var table = $(`#${tb.id}`).DataTable()
        var rows = table.rows({ "selected": true })
        for (row of rows[0]) {
          var tr = table.row(row).node()
          var input = $(tr).find("td:first-child input").clone()
          form.append(input)
          total += 1
        }
        table.rows().deselect()
      }
      if (total == 0) {
        fireToast("Selecione algum jogo para exportar!", "Atenção", "warning")
      }
      else {
        form.submit()
      }
      console.log(result)
    }
  })
}

$(document).ready(function () {
  show = true;
  fireMessagesToasts()
  setDataTables()
  $("#get-results-form").submit(handleResultsGeneration)
  $("#get-results-form input[name=lottery_name]").click(handleDrawsSelect)
  $(".send-results-btn").click(handleSendResults)
  $("#delete-results-btn").click(handleDeleteResults)
  $(".selectBox").click(showCheckboxes)
  $(".export-results-btn").click(handleExportResults)
  $(".export-results-reports-games-btn").click(handleExportResultGames)
  $("#create-game-set-btn").click(handleCreateGamesetFromSelected)
})