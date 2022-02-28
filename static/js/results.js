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
      $("#draw-number").html(`Nº ${draw.number} de ${draw.date}`)
      $("#draw-accumulated").html(draw.hasAccumulated ? "Sim" : "Não")
      $("#draw-result").html(`${draw.result.join(separator = "-")}`)
      var currency = { minimumFractionDigits: 2, style: 'currency', currency: 'BRL' }
      $("#draw-prize").html(draw.maxPrize.toLocaleString("pt-br", currency))
      $("#download-result-file").show()
      $("#download-result-file").html(
        `<span>Baixe o resultado gerado com os quantitativos abaixo. Clique no arquivo para baixar.</span>
      <a href="media/${filepath}" download><i class="fa fa-file-download h3 text-primary mx-3" id="filepath"></i></a>`
      )
      $("#n-jogos").html(total_balance["Numero de Jogos"])
      $("#value-paid").html(total_balance["Valor Gasto"].toLocaleString("pt-br", currency))
      $("#prizes-value").html(total_balance["Premiacao"].toLocaleString("pt-br", currency))
      $("#balance").html(total_balance["Saldo"].toLocaleString("pt-br", currency))
    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }

  })
})
