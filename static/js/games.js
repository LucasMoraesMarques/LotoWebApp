// General Initialisation
//import Swal from "sweetalert2"
//const Swal = require("sweetalert2")
var html = $("#gameset-form").html()
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
  $("#gamesets-table").DataTable({
    language: {
      lengthMenu: "Mostrar _MENU_ jogos por página",
      zeroRecords: "",
      info: "Página _PAGE_ de _PAGES_",
      infoEmpty: "Nenhum jogo encontrado",
      infoFiltered: "(Filtrados de _MAX_ jogod)",
      paginate: {
        previous: "←",
        next: "→",
      },
      searchPlaceholder: "Filtre por loteria, nome ou status",
      search: "Filtrar",
    },
    dom: "flrtip",
    columnDefs: [
      {
        orderable: false,
        className: "select-checkbox",
        targets: 0,
      },
    ],
    select: {
      style: "multi",
      selector: "td:first-child",
    },
  });


  $('#collections-table').DataTable({
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
    "dom": "frtip",
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
    "searchBuilder": true,
  });


  $('#collectionsTable_filter input[type="search"]').attr(
    'placeholder', "Busque por loteria, nome ou nº de jogos"
  )

  $('.dataTables_filter input[type="search"]').css(
    { 'width': '250px', 'display': 'inline-block' }
  );
});

function setCollectionGamesSetTable(){
  $('#collection-games-sets-table').DataTable({
    language: {
          "lengthMenu": "Mostrar _MENU_ conjuntos por página",
          "zeroRecords": "",
          "info": "Página _PAGE_ de _PAGES_",
          "infoEmpty": "Nenhum conjunto encontrado",
          "infoFiltered": "(Filtrados de _MAX_ conjuntos)",
          "paginate": {
            "previous": "←",
            "next": "→"
          },
          "searchPlaceholder": "Busque conjuntos por nome",
          "search": "Filtrar"
      },
      dom: "flrtip",
  });
  $('#collection-games-sets-table_filter').addClass("d-flex")
  $('#collection-games-sets-table_filter input[type="search"]').css(
    { 'width': '300px' }
  );
}
$('#collection-table-detail').DataTable({
  language: {
        "lengthMenu": "Mostrar _MENU_ conjuntos por página",
        "zeroRecords": "",
        "info": "Página _PAGE_ de _PAGES_",
        "infoEmpty": "Nenhum conjunto encontrado",
        "infoFiltered": "(Filtrados de _MAX_ conjuntos)",
        "paginate": {
          "previous": "←",
          "next": "→"
        },
        "searchPlaceholder": "Busque conjuntos por nome, loteria ou status",
        "search": "Filtrar"
    },
    dom: "flrtip",
});


// Generators Tab

function mapNumbers(cellId, op) { // Update grid of fixed and removed numbers
  console.log(op, cellId)
  let lottery = $("input[name='lottery_name']:checked").val()
  let nFixed = Array.from($("input[name='nFixed']:checked").map((ind, el) => { return parseInt(el.value) }))
  let nPlayedChosen = parseInt($("input[name=nPlayed]:checked").val())
  let nRemoved = Array.from($("input[name='nRemoved']:checked").map((ind, el) => { return parseInt(el.value) }))
  let nPossiblesList = lotteryInfo[lottery].nPossiblesList
  switch (op) {
    case "removed":
      if (nFixed.length < nPlayedChosen) {
        counterFixedId = cellId.replace(op, 'fixed');
        $("#label-".concat(counterFixedId)).toggleClass('disabled');
      }
      break;
    case "fixed":
      if (nRemoved.length < (nPossiblesList.length - nPlayedChosen)) {
        counterRemovedId = cellId.replace(op, 'removed');
        $("#label-".concat(counterRemovedId)).toggleClass('disabled')
      }

      break;
  }

}

function handleLotteryParams(lottery) { // Handle change in lottery type, updating nPlayed, grid fixed/removed and collections
  $("#check-nPlayed .reset-placeholder").hide()
  $("#grid-fixed .reset-placeholder").removeClass("d-flex")
  $("#grid-removed .reset-placeholder").removeClass("d-flex")
  $("#grid-removed .numbers").empty()
  $("#grid-fixed .numbers").empty()
  $("#check-nPlayed .numbers").empty()
  updateCollectionsSelect(lottery)
  updateNPlayedRadio(lottery)
  resetFixedAndRemovedGrids(lottery)
  updateFixedAndRemovedGrids()
  handleGeneratorSelect($("input[name=generator]:checked").get(0))
  $("#counters").show()
}

function updateNPlayedRadio(lottery) { // Update nPlayed options
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
}

function updateCollectionsSelect(lottery) {
  $("#collection-gen-select").children().map((ind, option) => { // Update collections
    if ($(option).attr("loto-name") == lottery) {
      $(option).show()
    }
    else {
      $(option).hide()
    }
  })
}

function resetFixedAndRemovedGrids(lottery) { // Reset fixed and removed numbers grids
  let nPossiblesList = lotteryInfo[lottery].nPossiblesList
  for (value of nPossiblesList) {
    $("#grid-fixed .numbers").append(
      `<div class="col">
          <input type="checkbox" class="btn-check" id="check-fixed-${value}"
            name="nFixed" value="${value}" autocomplete="off"
            onchange="mapNumbers(this.id, 'fixed')">
          <label class="btn btn-outline-success mb-2 disabled games-checkbox" for="check-fixed-${value}"
            id="label-check-fixed-${value}">${value}</label>
      </div>`
    )
  }

  for (value of nPossiblesList) {
    $("#grid-removed .numbers").append(
      `<div class="col">
          <input type="checkbox" class="btn-check" id="check-removed-${value}"
            name="nRemoved" value="${value}" autocomplete="off"
            onchange="mapNumbers(this.id, 'removed')">
          <label class="btn btn-outline-danger mb-2 disabled games-checkbox" for="check-removed-${value}"
            id="label-check-removed-${value}">${value}</label>
      </div>`
    )
  }

}

function updateFixedAndRemovedGrids() { // Callback to reset grids on nPlayed value change
  let nFixed = Array.from($("input[name='nFixed']:checked").map((ind, el) => { return parseInt(el.value) }))
  let nPlayedChosen = parseInt($("input[name=nPlayed]:checked").val())
  let nRemoved = Array.from($("input[name='nRemoved']:checked").map((ind, el) => { return parseInt(el.value) }))
  let lottery = $("input[name='lottery_name']:checked").val()
  let nPossiblesList = lotteryInfo[lottery].nPossiblesList
  if (nRemoved.length < (nPossiblesList.length - nPlayedChosen)) {
    nPossiblesList.map((ind, el) => {
      let value = parseInt(el) + 1
      if (!(nFixed.includes(value) || nRemoved.includes(value))) {
        $("label[for='check-removed-" + value + "']").removeClass('disabled');
      }
    })
  }
  else if ((nRemoved.length == (nPossiblesList.length - nPlayedChosen))) {
    nPossiblesList.map((ind, el) => {
      let value = parseInt(el) + 1
      if (!(nFixed.includes(value) || nRemoved.includes(value))) {
        $("label[for='check-removed-" + value + "']").addClass('disabled');
      }
    })
  }
  else {
    while (nRemoved.length > (nPossiblesList.length - nPlayedChosen)) {
      $("input[id='check-removed-" + nRemoved[0] + "']").prop("checked", false);
      $("label[for='check-removed-" + nRemoved[0] + "']").addClass('disabled');
      $("label[for='check-fixed-" + nRemoved[0] + "']").removeClass('disabled');
      nRemoved = Array.from($("input[name='nRemoved']:checked").map((ind, el) => { return parseInt(el.value) }))
    }
  }
  if (nFixed.length < nPlayedChosen) {
    nPossiblesList.map((ind, el) => {
      let value = parseInt(el) + 1
      if (!(nFixed.includes(value) || nRemoved.includes(value))) {
        $("label[for='check-fixed-" + value + "']").removeClass('disabled');
      }
    })
  }
  else if (nFixed.length == nPlayedChosen) {
    nPossiblesList.map((ind, el) => {
      let value = parseInt(el) + 1
      if (!(nFixed.includes(value) || nRemoved.includes(value))) {
        $("label[for='check-fixed-" + value + "']").addClass('disabled');
      }
    })
  }
  else {
    while (nFixed.length > nPlayedChosen) {
      $("input[id='check-fixed-" + nFixed[0] + "']").prop("checked", false);
      $("label[for='check-fixed-" + nFixed[0] + "']").addClass('disabled');
      $("label[for='check-removed-" + nFixed[0] + "']").removeClass('disabled');
      nFixed = Array.from($("input[name='nFixed']:checked").map((ind, el) => { return parseInt(el.value) }))
    }
  }

  if (!nRemoved.length && !nFixed.length) {
    nPossiblesList.map((ind, el) => {
      let value = parseInt(el) + 1
      console.log(nFixed.includes(value), nRemoved.includes(value))
      if (!(nFixed.includes(value) || nRemoved.includes(value)) && (nPlayedChosen)) {
        console.log("diff", value)
        $("label[for='check-fixed-" + value + "']").removeClass('disabled');
        $("label[for='check-removed-" + value + "']").removeClass('disabled');
      }
    })
  }
  console.log("here2")
  $("#counter-fixed").text(nFixed.length)
  $("#counter-removed").text(nRemoved.length)
}


function handleGeneratorSelect(radio) { // Handle generator type selection
  var nPlayedRadios = $("#check-nPlayed input[type=radio]")
  var nonDefaultValues = nPlayedRadios.filter((index, element) => { return index != 0 })

  if (radio.id == "smart") {
    $("#smart-gen-options").show()
    nonDefaultValues.map((index, element) => { $('#'.concat(element.id)).hide(); $('label[for='.concat(element.id, ']')).hide() })
  }
  else {
    $("#smart-gen-options").hide()
    nonDefaultValues.map((index, element) => { $('#'.concat(element.id)).show(); $('label[for='.concat(element.id, ']')).show() })

  }
}

function handleActionButtons(state) { // Handle which buttons appears in a given state
  var calcCombsBtn = $("#calc-combs-btn")
  var submitGeneratorForm = $("#submit-generator")
  var resetGeneratorForm = $("#reset-generator-form")
  var seeGameSet = $("#see-games-set")
  var counters = $("#counters")
  switch (state) {
    case "calc":
      calcCombsBtn.show();
      calcCombsBtn.addClass("disabled")
      submitGeneratorForm.hide();
      resetGeneratorForm.hide();
      seeGameSet.hide();
      counters.show()
      break;
    case "submit":
      calcCombsBtn.hide();
      submitGeneratorForm.show();
      resetGeneratorForm.show();
      seeGameSet.hide();
      $("#nJogos-input").show()
      counters.hide()
      break;
    case "see":
      calcCombsBtn.hide();
      submitGeneratorForm.hide();
      seeGameSet.show();
      resetGeneratorForm.show();
      counters.hide()
      break;
    case "reset":
      calcCombsBtn.hide();
      submitGeneratorForm.hide();
      seeGameSet.hide();
      resetGeneratorForm.show();
      handleGeneratorSelect($("input[name=generator]:checked").get(0))
      $("#counter-fixed").text(0)
      $("#counter-removed").text(0)
      counters.hide()
      break;
  }
}

function calcNumberOfCombinations() { // Calculate the number of combinations in the given generator form data
  spinner = createSpinnerLoading("Calculando combinações...")
  $("#actions-buttons").append(spinner)
  var nCombs = 0
  var generator = $("input[name='generator']:checked").val()
  var willCalcCombs = $("input[name='calcCombs']")
  var formData = $("#gerador-form").get(0)
  if (generator == "simple") {
    willCalcCombs.val("False")
    let lottery = formData["lottery_name"].value
    let nPlayed = parseInt(formData['nPlayed'].value)
    let nFixed = Array.from($("input[name='nFixed']:checked"))
    let nRemoved = Array.from($("input[name='nRemoved']:checked"))
    let m = lotteryInfo[lottery].nPossiblesList.length - nFixed.length - nRemoved.length
    let n = nPlayed - nFixed.length
    nCombs = math.combinations(m, n)
    showCombsInput(nCombs)
    $("#spinner").remove()
  }
  else {
    willCalcCombs.val("True")
    var serializedData = $(formData).serialize()
    $.ajax({
      type: "POST",
      url: "jogos/geradores",
      data: serializedData,
      success: function (response, nCombs) {
        nCombs = response["combs"]
        showCombsInput(nCombs)
        $("#spinner").remove()
      },
      error: function (response) {
        console.log(response)
        alert(response["responseJSON"]["error"]);
      }
    })
  }
}

function showCombsInput(nCombs) { // Show a number input to get nJogos
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

// jQuery callbacks and ajax

$('#check-nPlayed .numbers').change(function () { // Listen to changes in nPlayed
  updateFixedAndRemovedGrids()
})

$('#grid-fixed-removed').change(function () { // Listen to changes in nFixed or nRemoved
  updateFixedAndRemovedGrids()
})

$("#submit-generator").click(function () { // Handle if form submition is valid
  var nJogos = parseInt($("#nJogos-input").val())
  var nCombs = parseInt($("#nCombs").val())
  if (nJogos <= 0 | !nJogos) {
    fireToast("O número de jogos pedidos deve ser maior que zero e diferente de vazio. Tente novamente!", "Atenção", "warning")
  }
  else if (nJogos > nCombs) {
    fireToast("O número de jogos pedidos é maior que o número de combinação possíveis. Tente novamente!", "Atenção", "warning")
  }
  else {
    $("#gerador-form").submit()
  }

})

$("#gerador-form").submit(function (e) { // POST form and get generated jogos as response
  spinner = createSpinnerLoading("Gerando o conjunto de jogos ...")
  $("#actions-buttons").append(spinner)
  e.preventDefault()
  var serializedData = $(this).serialize()
  $.ajax({
    type: "POST",
    url: "jogos/geradores",
    data: serializedData,
    success: function (response) {
      $("#modal-content-gameset .modal-body").empty()
      $("#modal-content-gameset .modal-body").append(
        `<table id="table-jogos">
          <thead>
          </thead>
          <tbody>
          </tbody>
        </table>`)
      var cells = "<tr>"
      var data = JSON.parse(response["jogos"]);
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
      $("#spinner").remove()
    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }
  })
})

$("#reset-generator-form").click(function () { // Reset generator form completely
  $("#gerador-form").trigger("reset")
  $("input[name='ids']").remove()
  handleActionButtons("calc")
  $("#nJogos-input-div").hide()
  $("#table-jogos").remove()
  $("#check-nPlayed .reset-placeholder").show()
  $("#grid-fixed .reset-placeholder").addClass("d-flex")
  $("#grid-removed .reset-placeholder").addClass("d-flex")
  $("#grid-removed .numbers").empty()
  $("#grid-fixed .numbers").empty()
  $("#check-nPlayed .numbers").empty()
  $("#counter-fixed").text(0)
  $("#counter-removed").text(0)
  $("#counters").hide()
})

$("#gerador-form").change(function () { // Listen to changes on generator form and handle calc-combs-btn display
  var generator = $("input[name='generator']:checked").val()
  var lottery = $("input[name='lottery_name']:checked").val()
  let nPlayed = parseInt($("input[name=nPlayed]:checked").val())
  let nFixed = Array.from($("input[name='nFixed']:checked").map((ind, el) => { return parseInt(el.value) }))
  let nRemoved = Array.from($("input[name='nRemoved']:checked").map((ind, el) => { return parseInt(el.value) }))
  if (generator && lottery && nPlayed) {
    $("#calc-combs-btn").removeClass("disabled")
  }
  else {
    $("#calc-combs-btn").addClass("disabled")
  }
})

$("#save-gameset").click(function () { // Submit generator form again to save generated games
  let spinner = createSpinnerLoading("Salvando o jogo, não saia da página!")
  let modalFooterSaving = $(".modal-footer .saving")
  let modalFooterButtons = $(".modal-footer .buttons")
  modalFooterSaving.append(spinner).show()
  modalFooterButtons.toggleClass("d-flex").hide()
  modalFooterSaving.parent().addClass("justify-content-center")
  $("#gerador-form").attr("action", "/save-games-batch")
  $("#gerador-form").attr("method", "post")
  $("#gerador-form").off("submit")
  $("#gerador-form").submit()

})

// Collections Tab


$("#add-collection-form").submit(function (e) { // Add new collections 
  e.preventDefault()
  var serializedData = $(this).serialize()
  $.ajax({
    type: "POST",
    url: "jogos/colecoes/criar-colecao",
    data: serializedData,
    success: function (response) {
      $("#add-collection-form").trigger('reset')
      $("#close-add-collection").trigger('click')
      $("#gerador-form").trigger('reset')
      $("#collection-gen-select").prepend(
        `<option value="${response.id}" loto-name="${response.lottery}">${response.name}</option>`
      )
      Toast.fire({
        icon: 'success',
        title: "Sucesso!",
        text: `Coleção ${response.name} da loteria ${response.lottery} criada com sucesso`
      })

    },
    error: function (response) {
      console.log(response)
      alert(response.responseJSON["error"]);
    }

  })
})

$("#collection-file-form").submit(function (e) { // Handle file input to create collections
  e.preventDefault()
  var data = new FormData($(this).get(0));
  console.log(data)
  $.ajax({
    type: "POST",
    url: "jogos/colecoes/criar-colecao",
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

$(document).ready(function () {
  $(".messages p").each((ind, el) => {
    console.log(el)
    Toast.fire({
      icon: 'success',
      title: el.innerText
    })
  })
});



$("#delete-collections").click(function () {
  var action = this.innerText
  fireModal(
    `Você realmente deseja ${action} os coleções selecionadas?`,
    "Tem certeza ?",
    "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var table = $("#collections-table").DataTable()
      var rows = table.rows({ "selected": true })
      var form = $("#edit-collection")
      for (row of rows[0]) {
        var tr = table.row(row).node()
        var input = $(tr).find("td:first-child input")
        form.append(input)
      }
      $("#edit-collection input[name=action]").val(action)
      form.submit()
    }
    else if (answer.isDenied) {

    }
  })
})

function handleSendGamesSets() {
  var send_by = $(this).attr("data-send-by")
  fireModal(
    `Você realmente deseja enviar os conjuntos de jogos selecionados por ${send_by}?`,
    "Tem certeza ?",
    "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var table = $("#gamesets-table").DataTable();
      var rows = table.rows({ selected: true });
      var form = $("#send-games-sets-form");
      if (rows[0].length != 0) {
        for (row of rows[0]) {
          var tr = table.row(row).node();
          var input = $(tr).find("td:first-child input");
          form.append(input);
        }
        form.append(`<input name="method" value="${send_by}" type="hidden">`);
        form.submit();
      } else {
        fireToast(
          "Nenhum conjunto foi selecionado para envio. Clique nos botões na primeira coluna para selecionar",
          "Atenção",
          "warning"
        );
      }
    }
  });
}

function handleEditGamesSets() {
  var action = $(this).attr('data-action')
  Swal.fire({
    icon: "warning",
    title: "Tem certeza ?",
    text: `Você realmente deseja ${this.innerText} os conjuntos selecionados?`,
    showDenyButton: true,
    confirmButtonText: "SIM",
    denyButtonText: "NÃO",
    confirmButtonColor: "green",
    denyButtonColor: "red",
    customClass: {
      actions: 'my-actions',
      confirmButton: 'order-1',
      denyButton: 'order-2',
    }
  }).then((answer) => {
    if (answer.isConfirmed) {
      var table = $("#gamesets-table").DataTable()
      var rows = table.rows({ selected: true })
      var form = $("#edit-games-sets-form")
      for (row of rows[0]) {
        var tr = table.row(row).node()
        var input = $(tr).find("td:first-child input")
        form.append(input)
      }
      $("#edit-games-sets-form input[name=action]").val(action)
      $("#edit-games-sets-form").submit()
    }
    else if (answer.isDenied) {

    }
  })
}

function handleExportGamesSets() {
  var fileType = $(this).attr("data-export-by")
  fireModal(
    `Você realmente deseja EXPORTAR os conjuntos selecionados?`,
    "Tem certeza ?",
    "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var table = $("#gamesets-table").DataTable();
      var rows = table.rows({ selected: true });
      var form = $("#export-games-sets-form");
      for (row of rows[0]) {
        var tr = table.row(row).node();
        var input = $(tr).find("td:first-child input").clone();
        form.append(input);
      }
      form.append(`<input type="hidden" name="file-type" value="${fileType}">`);
      if (1 != 1) {
        fireToast(
          "Selecione somente resultados de uma única modalidade da loteria e exporte por loteria.",
          "Atenção",
          "warning"
        );
      } else {
        form.submit();
      }
      form.find("input").remove("[name=gamesets]");
      form.find("input").remove("[name=file-type]");
      table.rows().deselect();
    }
  });
}


function handleSendCollections() {
  var send_by = $(this).attr("data-send-by")
  var isDetailView = $("input[name=is_detail]").val()
  fireModal(
    isDetailView === 'False' ? `Você realmente deseja enviar as coleções de conjuntos selecionadas por ${send_by}?` : `Você realmente deseja enviar essa coleção por ${send_by}?`,
    "Tem certeza ?",
    "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var form = $("#send-collections-form");
      if (isDetailView === "False") {
        var table = $("#collections-table").DataTable();
        var rows = table.rows({ selected: true });
        if (rows[0].length != 0) {
          for (row of rows[0]) {
            var tr = table.row(row).node();
            var input = $(tr).find("td:first-child input");
            form.append(input);
          }
        } else {
          fireToast(
            "Nenhuma coleção foi selecionada para envio. Clique nos botões na primeira coluna para selecionar",
            "Atenção",
            "warning"
          );
        }
      }
      else{
        var collectionId = $("input[name=collection-id]").val()
        form.append($(`<input type="hidden" name="collections" value="${collectionId}">`))
      }
      form.append(`<input name="method" value="${send_by}" type="hidden">`);
      form.submit();

    }
  });
}

function handleEditCollections() {
  var action = $(this).attr('data-action')
  var isDetailView = $("input[name=is_detail]").val()
  fireModal(
    isDetailView === "False" ? `Você realmente deseja ${action} as coleções selecionadas?` : `Você realmente deseja ${action} esta coleção?`,
    "Tem certeza ?",
    "warning").then((answer) => {
    if (answer.isConfirmed) {
      var form = $("#edit-collections-form")
      if (isDetailView === "False") {
        var table = $("#collections-table").DataTable()
        var rows = table.rows({ selected: true })
        for (row of rows[0]) {
          var tr = table.row(row).node()
          var input = $(tr).find("td:first-child input")
          form.append(input)
        }
      }
      else{
        var collectionId = $("input[name=collection-id]").val()
        form.append($(`<input type="hidden" name="collections" value="${collectionId}">`))
      }
      $("#edit-collections-form input[name=action]").val(action)
      form.submit()
    }

  })
}

function handleExportCollections() {
  var fileType = $(this).attr("data-export-by")
  var isDetailView = $("input[name=is_detail]").val()
  fireModal(
    isDetailView === "False" ? `Você realmente deseja EXPORTAR as coleções selecionadas?` : `Você realmente deseja EXPORTAR essa coleção?`,
    "Tem certeza ?",
    "warning"
  ).then((answer) => {
    if (answer.isConfirmed) {
      var form = $("#export-collections-form");
      if( isDetailView === "False"){
        var table = $("#collections-table").DataTable();
        var rows = table.rows({ selected: true });
        for (row of rows[0]) {
          var tr = table.row(row).node();
          var input = $(tr).find("td:first-child input").clone();
          form.append(input);
        }
        table.rows().deselect();
      }
      else{
        var collectionId = $("input[name=collection-id]").val()
        form.append($(`<input type="hidden" name="collections" value="${collectionId}">`))
      }
      }
      form.append(`<input type="hidden" name="file-type" value="${fileType}">`);
      form.submit();
      form.find("input").remove("[name=collections]");
      form.find("input").remove("[name=file-type]");      
  });
}


function handleEditCollectionsGamesSets() {
  $("#gameset-form").remove()
  Swal.fire({
    title: "Escolha os conjuntos",
    html: html,
    showDenyButton: true,
    confirmButtonText: "SALVAR",
    denyButtonText: "CANCELAR",
    confirmButtonColor: 'green',
    focusConfirm: false,
    didRender: () => {
      setCollectionGamesSetTable()
    }
  }).then((result) => {
    if (result.isConfirmed) {
      $("#modify-collection input[name=action]").val("ADICIONAR")
      var collectionId = $("input[name=collection-id]").val()
      $("#modify-collection").append($(`<input type="hidden" name="collections" value="${collectionId}">`))
      $("#modify-collection").submit()
    }
  })
}

$(document).ready(function () {
  fireMessagesToasts();
  $(".send-games-sets-btn").click(handleSendGamesSets);
  $("#delete-results-btn").click(handleEditGamesSets);
  $(".export-games-sets-btn").click(handleExportGamesSets);
  $(".edit-games-sets-btn").click(handleEditGamesSets)

  $(".send-collections-btn").click(handleSendCollections);
  $(".export-collections-btn").click(handleExportCollections);
  $(".edit-collections-btn").click(handleEditCollections)

  $("#edit-collections-games-sets").click(handleEditCollectionsGamesSets)
});



