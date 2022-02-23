dt_options = {
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
            "pagingType": "simple",
            "searchPlaceholder": "Busque jogos por loteria, nome ou status",
            "search": "Filtrar"
        },
        "dom": "Bfrtip",
        "buttons": [
        {
        "extend": "collection",
            "text": "Exportar",
            "autoClose": true,
            "className": "btn btn-primary",
            "buttons":[
                {
                extend:    'excelHtml5',
                text:      '<i class="fa fa-file-excel fs-5"></i>',
                titleAttr: 'Exportar como Excel',
                className: "btn btn-secondary fs-5 px-3 py-2"
            },
            {
                extend:    'csvHtml5',
                text:      '<i class="fa fa-file-text fs-5"></i>',
                titleAttr: 'Exportar como CSV',
                className: "btn btn-secondary fs-5 px-3 py-2"
            },
            {
                extend:    'pdfHtml5',
                text:      '<i class="fa fa-file-pdf fs-5"></i>',
                titleAttr: 'Exportar como PDF',
                className: "btn btn-secondary fs-5 px-3 py-2"
            },
            {
                extend:    'print',
                text:      '<i class="fa fa-print fs-5"></i>',
                titleAttr: 'Imprimir tabela',
                className: "btn btn-secondary fs-5 px-3 py-2"
            }
            ]
            },

    ],
    }

$(document).ready(function() {
    $('.table').DataTable(dt_options);

    $('#collectionsTable_filter input[type="search"]').attr(
      'placeholder', "Busque por loteria, nome ou nº de jogos"
    )

    $('.dataTables_filter input[type="search"]').css(
     {'width':'300px','display':'inline-block'}
  );
    $(".buttons-collection").click(function(){
        $("div[role=menu]").addClass("mt-4")
    })

} );

    var win = navigator.platform.indexOf('Win') > -1;
    if (win && document.querySelector('#sidenav-scrollbar')) {
      var options = {
        damping: '0.5'
      }
      Scrollbar.init(document.querySelector('#sidenav-scrollbar'), options);
    }

$("input[name='select-lottery']").change(function(){
  var isChecked = $("input[name='select-lottery']:checked").val()
  console.log(isChecked)
  if( !isChecked ){
    $("#redirect").addClass("disabled")
  }
  else{
    $("#redirect").removeClass("disabled")
  }
})

function redirect(){
  window.location.href = "{% url 'lottery:loterias' %}" + $("input[name='select-lottery']:checked").val()

}

$("#get-combinations-form").submit(function (e) { // Get a ranking of combinations with size n
  e.preventDefault()
  var serializedData = $(this).serialize()
  spinner = createSpinnerLoading("Gerando combinações ...")
  $("#submit-combs-form-btn").hide()
  $("#div-combs-form").append(spinner)
  $.ajax({
    type: "GET",
    url: "/get-combinations",
    data: serializedData,
    success: function (response) {
      $(this).trigger('reset')
      console.log(response["combs"])
      var combs_table = $("#combs-table")
      var combs = response["combs"]
      var total = response["total"]
      combs_table.DataTable().destroy()
      combs_table.find("tbody").empty()
      for( comb of combs){
          var numbers = ""
          for(number of comb.numbers){
              numbers += `<span class="badge badge-sm bg-gradient-primary mx-1">${number}</span>`
          }
          combs_table.find("tbody").append(
          `
          <tr>
            <td class="text-center">${numbers}</td>
            <td>
                <p class="text-center text-xs font-weight-bold mb-0">${comb.repetitions}</p>
            </td>
          </tr>
          `
          )
      }
      combs_table.DataTable(dt_options)
      $('#collectionsTable_filter input[type="search"]').attr(
      'placeholder', "Busque por loteria, nome ou nº de jogos"
    )

    $('.dataTables_filter input[type="search"]').css(
     {'width':'300px','display':'inline-block'}
  );
  message = total + " combinações encontradas e as " + combs.length + " mais frequentes estão listadas abaixo."
  $("#n-combs-text").html(message)
  $("#spinner").remove()
  $("#submit-combs-form-btn").show()
  Toast.fire({
    icon: 'success',
    title: "Combinações geradas com sucesso!"
})
    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }

  })
})
