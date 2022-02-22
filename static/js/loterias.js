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
            "searchPlaceholder": "Busque jogos por loteria, nome ou status",
            "search": "Filtrar"
        },
        "dom": "Bfrtip",
        "buttons": [
        {
            "extend": "collection",
            "text": "Exportar",
            "autoClose": true,
            "className": "",
            "buttons":[
                {
                    "extend": "csv",
                    "text": "CSV",
                    "className": ""
                },
                {
                    "extend": "excel",
                    "text": "EXCEL",
                    "className": ""
                },
                {
                    "extend": "pdf",
                    "text": "PDF",
                    "className": ""
                },
                {
                    "extend": "print",
                    "text": "IMPRIMIR",
                    "className": ""
                }]
            },
            {
            "extend": "collection",
            "text": "Selecionar",
            "autoClose": true,
            "className": "",
            "buttons":[
                {
                    "extend": "selectAll",
                    "text": "Selecionar tudo",
                    "className": ""
                },
                {
                    "extend": "selectNone",
                    "text": "Limpar seleção",
                    "className": ""
                },
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
  console.log(serializedData)
  $.ajax({
    type: "GET",
    url: "/get-combinations",
    data: serializedData,
    success: function (response) {
      $(this).trigger('reset')
      console.log(response["combs"])
      var combs_table = $("#combs-table")
      var combs = response["combs"]
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
    },
    error: function (response) {
      console.log(response)
      alert(response["responseJSON"]["error"]);
    }

  })
})
