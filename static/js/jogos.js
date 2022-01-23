// General Initialisation

$(document).ready(function () {
  $("#menu").on('click', function () {
    $("#sidenav-main").fadeToggle(300)
  });

  $("#hide-message").on("click", function () {
    $("#messages").hide()
  })

  var win = navigator.platform.indexOf('Win') > -1;
  if (win && document.querySelector('#sidenav-scrollbar')) {
    var options = {
      damping: '0.5'
    }
    Scrollbar.init(document.querySelector('#sidenav-scrollbar'), options);
  }

  $('table.display').DataTable({
    language: {
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

    }
  });

  $('#collectionsTable_filter input[type="search"]').attr(
    'placeholder', "Busque por loteria, nome ou nº de jogos"
  )

  $('.dataTables_filter input[type="search"]').css(
    { 'width': '300px', 'display': 'inline-block' }
  );

  var lotteryInfo = new Object({
    lotofacil: {
      nPlayedList: Array.from(new Array(6), (x, i) => i + 15),
      nPossiblesList: Array.from(new Array(25), (x, i) => i + 1),
    },
    diadesorte: {
      nPlayedList: Array.from(new Array(9), (x, i) => i + 7),
      nPossiblesList: Array.from(new Array(31), (x, i) => i + 1),
    },
    megasena: {
      nPlayedList: Array.from(new Array(10), (x, i) => i + 6),
      nPossiblesList: Array.from(new Array(60), (x, i) => i + 1),
    }
  })
});


// Generators Tab

function mapNumbers(cellId, op) {
  console.log(op)
  switch (op) {
    case "removed":
      cellId = cellId.replace(op, 'fixed');
      console.log(cellId);
      $("#label-".concat(cellId)).toggleClass('disabled');
      break;

    case "fixed":
      cellId = cellId.replace(op, 'removed');
      console.log(cellId);
      $("#label-".concat(cellId)).toggleClass('disabled')
      break;
  }

}

function handleLotteryParams(lottery) {
  $("#check-nPlayed .reset-placeholder").hide()
  $("#grid-fixed .reset-placeholder").removeClass("d-flex")
  $("#grid-removed .reset-placeholder").removeClass("d-flex")
  $("#grid-removed .numbers").empty()
  $("#grid-fixed .numbers").empty()
  $("#check-nPlayed .numbers").empty()

  $("#collection-gen-select").children().map((ind, el) => {
    console.log($(el).attr("loto-name"), lottery)
    if ($(el).attr("loto-name") == lottery) {
      $(el).show()
    }
    else {
      $(el).hide()
    }
  })

  for (value of lotteryInfo[lottery].nPlayedList) {
    $("#check-nPlayed .numbers").append(
      `<div class="form-check" id="check-n-{{value}}}">
           <input class="form-check-input mx-2" type="radio" id="check-played-${value}" name="nPlayed"
              value="${value}" required>
           <label class="custom-control-label fs-6" for="check-played-${value}">${value}</label>
           </div>
           `
    )
  }

  $('#check-nPlayed .numbers').change(function () {
    $("input[name='nFixed']").map((ind, el) => {
      $("label[for='" + el.id + "']").removeClass('disabled');
    })

    $("input[name='nRemoved']").map((ind, el) => {
      $("label[for='" + el.id + "']").removeClass('disabled');
    })
    $('#check-nPlayed').off()
    $('#check-nPlayed').change(function () {
      //checkSumOfChecksLTnPlayed()
    })
  })


  for (value of lotteryInfo[lottery].nPossiblesList) {
    $("#grid-fixed .numbers").append(
      `<div class="col">
          <input type="checkbox" class="btn-check" id="check-fixed-${value}"
            name="nFixed" value="${value}" autocomplete="off"
            onchange="mapNumbers(this.id, 'fixed')">
          <label class="btn btn-outline-success mb-2 disabled" for="check-fixed-${value}"
            style="padding:3px 3px; width:40px; height:40px; font-size:20px;"
            id="label-check-fixed-${value}">${value}</label>
      </div>`
    )
  }


  for (value of lotteryInfo[lottery].nPossiblesList) {
    $("#grid-removed .numbers").append(
      `<div class="col">
          <input type="checkbox" class="btn-check" id="check-removed-${value}"
            name="nRemoved" value="${value}" autocomplete="off"
            onchange="mapNumbers(this.id, 'removed')">
          <label class="btn btn-outline-danger mb-2 disabled" for="check-removed-${value}"
            style="padding:3px 3px; width:40px; height:40px; font-size:20px;"
            id="label-check-removed-${value}">${value}</label>
      </div>`
    )
  }
  handleGeneratorSelect($("input[name=generator]:checked").get(0))
}

function handleGeneratorSelect(radio) {
  console.log(radio.id)
  var nPlayedRadios = $("#check-nPlayed input[type=radio]")
  var np = nPlayedRadios.filter((index, element) => { return index != 0 })

  if (radio.id == "smart") {
    $("#smart-gen-options").show()
    np.map((index, element) => { $('#'.concat(element.id)).hide(); $('label[for='.concat(element.id, ']')).hide() })
  }
  else {
    $("#smart-gen-options").hide()
    np.map((index, element) => { $('#'.concat(element.id)).show(); $('label[for='.concat(element.id, ']')).show() })

  }
}

function handleActionButtons(state) {
  var calcCombsBtn = $("#calc-combs-btn")
  var submitGeneratorForm = $("#submit-generator")
  var resetGeneratorForm = $("#reset-generator-form")
  var seeGameSet = $("#see-games-set")
  switch (state) {
    case "calc":
      calcCombsBtn.show();
      calcCombsBtn.addClass("disabled")
      submitGeneratorForm.hide();
      resetGeneratorForm.hide();
      seeGameSet.hide();
      break;
    case "submit":
      calcCombsBtn.hide();
      submitGeneratorForm.show();
      resetGeneratorForm.show();
      seeGameSet.hide();
      $("#nJogos-input").show()
      break;
    case "see":
      calcCombsBtn.hide();
      submitGeneratorForm.hide();
      seeGameSet.show();
      resetGeneratorForm.show();
      break;
    case "reset":
      calcCombsBtn.hide();
      submitGeneratorForm.hide();
      seeGameSet.hide();
      resetGeneratorForm.show();
      break;
  }
}

function calcNumberOfCombinations() {
  var nCombs = 0
  var generator = $("input[name='generator']:checked").val()
  var willCalcCombs = $("input[name='calcCombs']")
  var formData = $("#gerador-form").get(0)
  if (generator == "simple") {
    willCalcCombs.val("False")
    let lottery = formData["lototype"].value
    let nPlayed = parseInt(formData['nPlayed'].value)
    let nFixed = Array.from($("input[name='nFixed']:checked"))
    let nRemoved = Array.from($("input[name='nRemoved']:checked"))
    let m = lotteryInfo[lottery].nPossiblesList.length - nFixed.length - nRemoved.length
    let n = nPlayed - nFixed.length
    nCombs = math.combinations(m, n)
    $("#nJogos-input-div").show()
    $("#nCombs-span").text("O número de combinações possíveis é " + nCombs)
    if (nCombs != 0) {
      handleActionButtons("submit")
      $("#nCombs").val(nCombs)
      $("input[name='calcCombs']").val("False")
    }
    else {
      handleActionButtons("reset")
    }
  }
  else {
    willCalcCombs.val("True")
    var serializedData = $(formData).serialize()
    $.ajax({
      type: "POST",
      url: "jogos/generator",
      data: serializedData,
      success: function (response, nCombs) {
        nCombs = response["combs"]
        $("#nJogos-input-div").show()
        $("#nCombs-span").text("O número de combinações possíveis é " + nCombs)
        if (nCombs != 0) {
          handleActionButtons("submit")
          $("#nCombs").val(nCombs)
          $("input[name='calcCombs']").val("False")
        }
        else {
          handleActionButtons("reset")
        }
      },
      error: function (response) {
        console.log(response)
        alert(response["responseJSON"]["error"]);
      }
    })
  }
}


function checkSumOfChecksLTnPlayed() {
  let nFixedChosen = Array.from($("input[name='nFixed']:checked"))
  let nPlayedChosen = parseInt(document.forms['gerador-form']['nPlayed'].value)
  let nRemovedChosen = Array.from($("input[name='nRemoved']:checked"))
  let sum = nFixedChosen.length + nRemovedChosen.length
  console.log(sum)
  if (sum == nPlayedChosen) {
    $("input[name='nFixed']").map((ind, el) => {
      $("label[for='" + el.id + "']").addClass('disabled');
    })
    $("input[name='nRemoved']").map((ind, el) => {
      $("label[for='" + el.id + "']").addClass('disabled');
    })
  }
  else {
    $("input[name='nFixed']").map((ind, el) => {
      $("label[for='" + el.id + "']").removeClass('disabled');
    })
    $("input[name='nRemoved']").map((ind, el) => {
      $("label[for='" + el.id + "']").removeClass('disabled');
    })
  }
}


$("#submit-generator").click(function () {
  var nJogos = parseInt($("#nJogos-input").val())
  var nCombs = parseInt($("#nCombs").val())
  console.log(nCombs, nJogos)
  if (nJogos <= 0 | !nJogos) {
    $("#messages").show()
    $("#messages span.alert-text").text("O número de jogos pedidos deve ser maior que zero e diferente de vazio. Tente novamente!")
    $("#messages").removeClass("alert-success")
    $("#messages").addClass("alert-danger")
  }
  else if (nJogos > nCombs) {
    $("#messages").show()
    $("#messages span.alert-text").text("O número de jogos pedidos é maior que o número de combinação possíveis. Tente novamente!")
    $("#messages").removeClass("alert-success")
    $("#messages").addClass("alert-danger")
  }
  else {
    $("#gerador-form").submit()
  }

})
$("#gerador-form").submit(function (e) {
  e.preventDefault()
  var serializedData = $(this).serialize()
  var data = $(this).get(0)
  var collection = data["collection-gen-select"].value
  var gameset = data["gameset-name"].value
  var lottery = data["lototype"].value
  $.ajax({
    type: "POST",
    url: "jogos/generator",
    data: serializedData,
    success: function (response) {
      $("#modal-content-gameset .modal-body").empty()
      $("#modal-content-gameset .modal-body").append(
        `
      <table id="table-jogos">
          <thead>
          </thead>
          <tbody>
          </tbody>
      </table>
      `
      )
      var cells = "<tr>"
      var data = JSON.parse(response["jogos"]);
      console.log(response)
      var ids = response["ids"]
      for (let i = 1; i < data.columns.length + 1; i++) {
        cells += `<th class="mx-3">Bola ${i}</th>`
      }
      cells += '</tr>'
      $("#table-jogos thead").append(cells)
      for (let i in data['data']) {
        cells = '<tr class="text-center">'
        for (let j in data['data'][i]) {
          cells += `<td>${data['data'][i][j]}</td>`
        }
        cells += '</tr>'
        $("#table-jogos tbody").append(cells)
      }
      cells = ""
      for (let i in ids) {
        cells += `<input type="hidden" name="ids" value=${ids[i]}>`
      }
      $("#gerador-form").append(cells)
      $("#table-jogos").DataTable()
      handleActionButtons("see")
    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }
  })
})

$("#reset-generator-form").click(function () {
  $("#gerador-form").trigger("reset")
  $("input[name='ids']").remove()
  checkSumOfChecksLTnPlayed()
  handleActionButtons("calc")
  $("#nJogos-input-div").hide()
  $("#table-jogos").remove()
  $("#check-nPlayed .reset-placeholder").show()
  $("#grid-fixed .reset-placeholder").addClass("d-flex")
  $("#grid-removed .reset-placeholder").addClass("d-flex")
  $("#grid-removed .numbers").empty()
  $("#grid-fixed .numbers").empty()
  $("#check-nPlayed .numbers").empty()
})

$("#gerador-form").change(function () {
  var generator = $("input[name='generator']:checked").val()
  var lottery = $("input[name='lototype']:checked").val()
  var nPlayed = $("input[name='nPlayed']:checked").val()
  if (generator && lottery && nPlayed) {
    $("#calc-combs-btn").removeClass("disabled")
  }
  else {
    $("#calc-combs-btn").addClass("disabled")
  }
})

$("#save-gameset").click(function () {
  $("#modal-content-gameset .modal-footer .saving").append(`
  <div class="spinner-border text-primary mx-3" role="status">
</div>
  <p>Salvando o jogo, não saia da página!</p>
  `)
  $("#modal-content-gameset .modal-footer .saving").addClass("d-flex", "flex-row")
  $("#modal-content-gameset .modal-footer .saving").show()

  $("#modal-content-gameset .modal-footer .buttons").toggleClass("d-flex")
  $("#modal-content-gameset .modal-footer .buttons").hide()
  $("#modal-content-gameset .modal-footer").addClass("justify-content-center")
  $("#gerador-form").attr("action", "/save-games-batch")
  $("#gerador-form").attr("method", "post")
  $("#gerador-form").off("submit")
  $("#gerador-form").submit()

})

// Collections Tab


$("#add-collection-form").submit(function (e) {
  e.preventDefault()
  var serializedData = $(this).serialize()
  console.log(serializedData)
  $.ajax({
    type: "POST",
    url: "jogos/colecoes/create-collection",
    data: serializedData,
    success: function (response) {
      $("#add-collection-form").trigger('reset')
      $("#close-add-collection").trigger('click')
      $("#gerador-form").trigger('reset')
      $("#collection-gen-select").prepend(
        `<option value="${response.id}" loto-name="${response.lottery}">${response.name}</option>`
      )
      $("#messages").show()
      $("#messages span.alert-text").text(`Coleção ${response.name} da loteria ${response.lottery} criada com sucesso`)


    },
    error: function (response) {
      console.log(response)
      alert(response.responseJSON["error"]);
    }

  })
})

$("#collection-file-form").submit(function (e) {
  e.preventDefault()
  var data = new FormData($(this).get(0));
  console.log(data)
  $.ajax({
    type: "POST",
    url: "jogos/colecoes/create-collection",
    cache: false,
    contentType: false,
    processData: false,
    data: data,
    success: function (response) {
      $("#add-collection-form").trigger('reset')
      $("#close-add-collection").trigger('click')
      $("#collection-gen-select").prepend(
        `<option value="${response.id}">${response.name}</option>`
      )
      $("#messages").show()
      $("#messages span.alert-text").text(`Coleção ${response.name} da loteria ${response.lottery} criada com sucesso`)


    },
    error: function (response) {
      console.log(response)
      alert(response.responseJSON["error"]);
    }

  })
})


// Draws Tab

$("input[name=lototype2]").on("click", function () {
  $.ajax({
    type: "GET",
    url: `get-draw?lottery=${this.value}`,
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

    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }

  })
})


$("#get-results-form").submit(function (e) {
  e.preventDefault()
  var serializedData = $(this).serialize()
  console.log(serializedData)

  $.ajax({
    type: "POST",
    url: "/get-draw",
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