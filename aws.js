/**
 * 
 */


var data = d3.json('fastly-billing.json', function(error, data){
	function tabulate(data, columns) {
		var table = d3.select('body').append('table')
		var thead = table.append('thead')
		var tbody = table.append('tbody');
		
		//data.sort(function(x,y) {
			//return d3.ascending(x["Service Cost $"], y["Service Cost $"]);
		//}
				//)
		
		data.sort(function(a,b) {
			return +parseInt(b["Service Cost"]) - (+parseInt(a["Service Cost"]));
		})
		
		
		
		
		//append the header row
		thead.append('tr')
			.selectAll('th')
			.data(columns).enter()
			.append('th')
				.text(function(column){ return column; });
		
		//create a row for each object in the data
		var rows = tbody.selectAll('tr')
			.data(data) //turned data to view data
			.enter()
			.append('tr');
		
		//create a cell in each row for each column
		var cells = rows.selectAll('td')
			.data( function (row) {
				return columns.map(function (column) {
					return {column: column, value: row[column]};
				});
			})
			.enter()
			.append('td')
				.text(function (d) { return d.value; });
		
		/**
		var margin = {top: 20};
		buttonNames = ["prev", "next"]
		var tbutton = tbody.selectAll("input")
			.data(buttonNames).enter().append("input")
			.attr("type", "button")
			.attr("class","button")
			.attr("value", function (d) {return d;}) */
				
		return table;
	}
	//delete from here if need be
	 
	 
	 
	
	//render table
	tabulate(data,['Name', 'Service ID', 'Bandwidth Cost', 'Request Cost', 'Service Cost']);
}); //end of method
