<?php
	$config=array();
	$config["version"]="v1";
	$config["enableLogFile"]=true;
	$config["defaultCurrency"]="€";
	$config["defaultCurrencyTxt"]="EUR";
	$config["host"]="www.unioncucine.it/takeaway-manager";
	
	$config["enableLogBacktrace"]=false;
	$config["expiringLoginCredential"]=30;
	$config["platform-code"]="unioncucine-takeaway";
	$config["name"]="Unioncucine Takeaway";
	$config["showAllCat"]=true;
	$config["baseurl"]="https://".$config["host"];
	$config["websiteurl"]=$config["baseurl"]."/web";
	$config["websiteurl"]=$config["baseurl"]."";
	
	$config["localpath"]=$_SERVER["DOCUMENT_ROOT"]."/takeaway-manager/";
	$config["localServicePath"]=$config["localpath"]."service/".$config["version"]."/";
	$config["respath"]=$config["localpath"]."/res/";
	$config["resurlpath"]=$config["baseurl"]."/res/";
	$config["mediapath"]=$config["baseurl"]."/res/media/";
	$config["localmediapath"]="/res/media/";

	$config["registerType"]=array("horeca"=>6,"manufacturer"=>7);
	$config["registerDefaultType"]="horeca";
	$config["defaultImageUrl"]=$config["baseurl"]."/res/categories/0.jpg";
	$config["dirImageUrl"]=$config["baseurl"]."/res/folder.png";
	$config["db_prefix"]="cf1_";
	$config["defaultLang"]=1;
	$config["lang"]=1;
	$config["encryptedPassword"]=true;
	$config["distance_default"]=10;
	$config["path"]=$config["baseurl"]."/service/".$config["version"]."/";
	$config["paypal_link"]="https://api.sandbox.paypal.com/v1/payments/payment";
	$config["paypal_login"]="https://api.sandbox.paypal.com/v1/oauth2/token";
	$config["link"]=$config["baseurl"]."/admin/";
	$config["stati"]=array();
	$config["statiPagamento"]=array(0=>"Non pagato",1=>"Pagamento completato",2=>"Pagamento rifiutato",3=>"Pagamento rimborsato",4=>"Da contabilizzare");
	$config["stati"][0]=array("label"=>"Annullato","color"=>"#FF0000");
	$config["stati"][10]=array("label"=>"Da processare","color"=>"#FF8000");
//	$config["stati"][20]=array("label"=>"In attesa di pagamento","color"=>"#FF0000");
//	$config["stati"][25]=array("label"=>"Verifica pagamento","color"=>"#FF0000");
	$config["stati"][30]=array("label"=>"In preparazione","color"=>"#FF8000");
	$config["prodottoAggiunto"]="Product added to your cart correctly";	
	$config["prodottoNonAggiunto"]="Invalid product";
	$config["stati"][40]=array("label"=>"Evaso","color"=>"#FF8000");
	$config["stati"][35]=array("label"=>"Evaso parzialmente","color"=>"#FF8000");
	$config["stati"][50]=array("label"=>"Consegnato","color"=>"#00FF00");
	$config["stati"][90]=array("label"=>"Annullato","color"=>"#00FF00");
	$config["mesi"]=array();
	$config["mesi"][]="Gennaio";
	$config["mesi"][]="Febbraio";
	$config["mesi"][]="Marzo";
	$config["mesi"][]="Aprile";
	$config["mesi"][]="Maggio";
	$config["mesi"][]="Giugno";
	$config["mesi"][]="Luglio";
	$config["mesi"][]="Agosto";
	$config["mesi"][]="Settembre";
	$config["mesi"][]="Ottobre";
	$config["mesi"][]="Novembre";
	$config["mesi"][]="Dicembre";
	$config["timeout"]=array();
	$config["timeout"]["sessioniUtente"]=60*60*24*1; /* secondi * minuti * ore* giorni ->1 giorni */
	$config["timeout"]["sessioni"]=60*60*24*1; /* 1 giorno */
	$config["membership_cat"]=1277;
	$config["timeout"]["backup"]=60*60*24*1; /* 1 giorno, backup giornaliero */
	$config["backupLocal"]="bak/";
	$config["serviziList"]=array("Ristoranti"=>"Ristoranti", "Market"=>"Market","Hotel"=>"Hotel","Distributori"=>"Distributori");
	$config["ivaList"]=array(0=>"Iva esente", 4=>"Iva 4%",10=>"Iva 10%",22=>"Iva 22%");
	$config["backupLocalPath"]=$config["backupLocal"].date("Y-m-d");
	$config["backupPath"]=$config["localpath"].$config["backupLocalPath"];
	$config["logPath"]=$config["localpath"]."service/".$config["version"]."/log/";
	$config["backupExclude"]=array();
	$config["backupExclude"][]="/www/".$config["backupLocal"];
	$config["backupExclude"][]="/www/wp/";
	$config["backupExclude"][]="/www/test/";
	$config["backupExclude"][]="/www/manager/";
	$config["backupExclude"][]="/www/website/";
	$config["backupExclude"][]="/www/fm/";
	$config["backupExclude"][]="/www/dbAdmin/";
	$config["backupLink"]=$config["baseurl"]."/".$config["backupLocalPath"];
	$config["defaultPermission"]=0775;
	$config["ordineCliente"]="Nuovo ordine da cliente";
	$config["ordineWeb"]="Nuovo ordine Takeway nr.";
	$config["defaultCategoryIcon"]="icn_categories";
	$config["defaultGroupMenu"]="Altro";
	
	$config["emailFullSender"]="From: ".$config["emailSenderName"]." <".$config["emailSender"].">\r\n";
	$config["search_producer_with_products"]=false;
	$config["upload"]=array();
	
	/* GOOGLE MAP KEY*/	
	$config["key"]="";
	$config["sensor"]="false";
	$config["defaultZoom"]="10";
	$config["firmaMail"]="\r\n\r\nGrazie,\r\n\r\Unioncucine Staff";
	$config["charArray"]=array("a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","x","y","w","z","0","1","2","3","4","5","6","7","8","9");
	$config["valuteService"]="http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20(%SPAZIO_VALUTE%)&env=store://datatables.org/alltableswithkeys&format=json";
	$config["templateDir"]="template/";
	$config["genericOrderTemplate"]="order-unioncucine";
	$config["customerOrderTemplate"]=null;
	$config["producerOrderTemplate"]=null;
	$defaultBookingCondition=array(
					"time"=>"16:30",
					"targetDay"=>"-1",
					"weekdayRules"=>array(
						0=>array(
							"time"=>"16:30",
							"targetDay"=>"-2"
						)
					)

				);
	$config["closingChristmasDays"]=array(


		"2023-12-23"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-25"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-26"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-26"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-27"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-28"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-29"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2023-12-30"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
		
		"2024-01-01"=>array(
			"time"=>"16:00",
			"targetDay"=>"-20"
		),
	);
	$config["disabledApril2025Days"]=array(
	
	
		"2025-03-28"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-03-31"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-01"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-02"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-03"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-04"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-07"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-08"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-09"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-10"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-11"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-14"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-15"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-16"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-17"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		),
		
		"2025-04-18"=>array(
			"time"=>"16:00",
			"targetDay"=>"-1000"
		)
	)
		;
	$config["menu-tipo-rules"]=array(
		// questo è il livello SEDE 1 agrate 2 cornaredo 3 colleoni 4 dnp 5 gastroshop
		1=>array(
			// 0 menu normale, 1 panini
			0=>array(
				"allowedTurn"=>array(1=>true,2=>true,3=>true,4=>true,7=>false),
				"allowedWeekDays"=>array(0,1,2,3,4,5,6),
				//"turnHourCondition"=>array(1=>$defaultBookingCondition,2=>$defaultBookingCondition,3=>$defaultBookingCondition,4=>$defaultBookingCondition),
				"hourVisibilityCondition"=>$defaultBookingCondition,
				

			),
			1=>array(
				
				"allowedTurn"=>array(1=>true,2=>true,3=>true,4=>true,7=>false),
				"turnHourCondition"=>array(
					
					1=>array(
						"time"=>"10:00",
						"targetDay"=>"+0",
						"validSpecificDays"=>$config["disabledApril2025Days"]
					),
					2=>array(
						"time"=>"16:30",
						"targetDay"=>"+0"
					),
					3=>array(
						"time"=>"16:30",
						"targetDay"=>"+0"
					),
					4=>array(
						"time"=>"10:00",
						"targetDay"=>"+0",
						
						"validSpecificDays"=>$config["disabledApril2025Days"],
						"weekdayRules"=>array(
							0=>null
						)
					)

				),
				"allowedWeekDays"=>array(0,1,2,3,4,5,6)
			)
		),
		2=>array( 
			// CORNAREDO
			// 5 quadrifoglio
			// 6 primo e giornata
			// 9 secondo turno
			// 14 notte
			0=>array(
				"allowedTurn"=>array(5=>true,6=>true,9=>false,14=>false),
				"allowedWeekDays"=>array(0,1,2,3,4,5,6),
				"hourVisibilityCondition"=>array(
					"time"=>"16:30",
					"targetDay"=>"-1"
				),
				"turnHourCondition"=>array(
					5=>array( /* cornaredo quadrifoglio */
						"time"=>"16:30",
						"targetDay"=>"-1",
						"weekdayRules"=>array(
							// tutti i giorni tranne sabato e domenica
							0=>null,
							6=>null
						)
							
					),
					6=>array( /* cornaredo primo e giornata */
						"time"=>"16:30",
						"targetDay"=>"-1",
						"weekdayRules"=>array(
							// tutti i giorni tranne sabato, domenica si prenota fino al venerdi alle 12 (-2 dd)
							0=>array(
								"time"=>"12:00",
								"targetDay"=>"-2"
							),	
							6=>null
						)
							
					),
					

				),

			),
			1=>array(

				"allowedTurn"=>array(5=>true,6=>true,9=>false,14=>false),
				"allowedWeekDays"=>array(1,2,3,4,5,6),
				"turnHourCondition"=>array(
					5=>array( /* cornaredo QUADRIFOGLIO */
						"time"=>"10:00",
						"targetDay"=>"+0",
						"weekdayRules"=>array(
							6=>null
						),
						"validSpecificDays"=>$config["closingChristmasDays"]
					),
					6=>array( /* cornaredo MENSA giornata e primo turno */
						"time"=>"10:00",
						"targetDay"=>"+0",
						
						"validSpecificDays"=>$config["closingChristmasDays"]
					),
					9=>array( /* cornaredo secondo turno */
						"time"=>"16:30",
						"targetDay"=>"+0",
						"weekdayRules"=>array(
							6=>array(
								"time"=>"16:30",
								"targetDay"=>"-3650"
							)
						),
						
						"validSpecificDays"=>$config["closingChristmasDays"]
							
					),
					

				),
			)
		),
		3=>array(
			0=>array(
				"allowedTurn"=>array(8=>true),
				"allowedWeekDays"=>array(0,1,2,3,4,5),
				"hourVisibilityCondition"=>array(
					"time"=>"16:30",
					"targetDay"=>"-1"
				),
				

			),
			1=>array(

				"allowedTurn"=>array(8=>true),
				"allowedWeekDays"=>array(1,2,3,4,5),
				"hourVisibilityCondition"=>array(
					"time"=>"10:00",
					"targetDay"=>"+0",
					
					"validSpecificDays"=>$config["disabledApril2025Days"],
				),
			)
		),
		4=>array(
			// 0 menu normale, 1 panini
			0=>array(

				"allowedTurn"=>array(10=>true,11=>true,12=>true), //10 primo turno, 11 secondo, 12 terzo
				"allowedWeekDays"=>array(0,1,2,3,4,5,6),
				"turnHourCondition"=>array(
					10=>array( /* DNP 1° */
						"time"=>"16:00",
						"targetDay"=>"-1",
						"validSpecificDays"=>array(
							
							"2025-01-06"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							
							"2025-04-21"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							
							"2025-04-25"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							
							"2025-05-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							"2025-06-02"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							
							"2025-08-15"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							
							"2025-12-08"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							"2025-12-26"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							"2026-01-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1000"
							),
							
							"2026-01-06"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							"2026-04-06"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							"2026-05-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
						),
						"weekdayRules"=>array(
							1=>null,
							2=>null,
						
							3=>null,
							4=>null,

							5=>null,
							0=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							)
						)
					),
					11=>array( /* DNP 2° */
						"time"=>"16:00",
						"targetDay"=>"-1",
						"weekdayRules"=>array(
							0=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							)
						),
						"validSpecificDays"=>array(


							"2023-12-24"=>array(
								"time"=>"16:00",
								"targetDay"=>"-24"
							),
							"2023-12-31"=>array(
								"time"=>"16:00",
								"targetDay"=>"-24"
							),
							"2024-04-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							"2024-04-25"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							
							"2024-05-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							"2024-12-26"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							
							"2025-01-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							
							"2025-01-06"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							
							"2025-12-26"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							
							"2026-01-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
						)
					),
					12=>array( /* DNPP 3° */
						"time"=>"16:00",
						"targetDay"=>"-1",
						"weekdayRules"=>array(
							0=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							)
						),
						"validSpecificDays"=>array(


							"2023-12-24"=>array(
								"time"=>"16:00",
								"targetDay"=>"-24"
							),
							"2023-12-31"=>array(
								"time"=>"16:00",
								"targetDay"=>"-24"
							),
							"2024-04-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							"2024-04-25"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							
							"2024-05-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
							"2024-12-26"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							"2025-01-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							
							"2025-01-06"=>array(
								"time"=>"16:00",
								"targetDay"=>"-3"
							),
							
							"2025-12-26"=>array(
								"time"=>"16:00",
								"targetDay"=>"-2"
							),
							
							"2026-01-01"=>array(
								"time"=>"16:00",
								"targetDay"=>"-1"
							),
						)
					),
					

				),
			),	
			1=>array(
				"allowedTurn"=>array(),
				"allowedWeekDays"=>array(),
				//"turnHourCondition"=>array(1=>$defaultBookingCondition,2=>$defaultBookingCondition,3=>$defaultBookingCondition,4=>$defaultBookingCondition),
				"hourVisibilityCondition"=>$defaultBookingCondition,
				

			)
		),
		5=>array(
			// 0 menu normale, 1 panini
			0=>array(

				"allowedTurn"=>array(13=>true),
				"allowedWeekDays"=>array(1,2,3,4,5),
				"hourVisibilityCondition"=>array(
					"time"=>"10:00",
					"targetDay"=>"0",
			/*		"weekdayRules"=>array(
						0=>array(
							"time"=>"16:30",
							"targetDay"=>"-2"
						)
					)*/

				),
			),	
			1=>array(
				"allowedTurn"=>array(),
				"allowedWeekDays"=>array(),
				//"turnHourCondition"=>array(1=>$defaultBookingCondition,2=>$defaultBookingCondition,3=>$defaultBookingCondition,4=>$defaultBookingCondition),
				"hourVisibilityCondition"=>$defaultBookingCondition,
				

			)
		),
		6=>array( 
			// CORNAREDO TURNISTI
			// 5 quadrifoglio
			// 6 primo e giornata
			// 9 secondo turno
			// 14 notte
			0=>array(
				"allowedTurn"=>array(9=>true,14=>true),
				"allowedWeekDays"=>array(0,6), // 02/10/26 sabato domenica
				"hourVisibilityCondition"=>array(
					"time"=>"16:30",
					"targetDay"=>"-1"
				),
				"turnHourCondition"=>array(				
					
					9=>array( /* cornaredo secondo turno */
						"time"=>"16:30",
						"targetDay"=>"-1",
						"weekdayRules"=>array(
						
							0=>array(
								"time"=>"12:00",
								"targetDay"=>"-2"
							),	
							1=>null,
							2=>null,
							3=>null,
							4=>null,
							5=>null,
							6=>array(
								"time"=>"12:00",
								"targetDay"=>"-1"
							)
						)
							
					),
					14=>array( /* cornaredo notte */
						"time"=>"16:30",
						"targetDay"=>"-1",
						"weekdayRules"=>array(
							0=>array(
								"time"=>"12:00",
								"targetDay"=>"-2"
							),	
							
							6=>array(
								"time"=>"12:00",
								"targetDay"=>"-1"
							)
						),					
							
					),

				),

			)
		)
	);
	$config["company-data"]=array(
		"name"=>"Unioncucine S.n.c.",
		"address"=>"via Boccaccio, 120",
		"cap"=>"20099",
		"city"=>"Sesto San Giovanni",
		"prov"=>"MI",
		"codfis"=>"04076310152",
		"piva"=>"00770030963",
		"tel"=>"039/6855049",
		"email"=>"unioncucine@iol.it",
		"logo"=>"https://www.unioncucine.it/images/logo1.png"
	);
	

?>