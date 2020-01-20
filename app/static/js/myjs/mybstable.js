 
  "use strict";
  function test_button(){
    let rowdata = JSON.stringify($table.bootstrapTable('getData')[1]);
    console.log(rowdata);
  }
    
  function save_all(){
    //let table_data = JSON.stringify($table.bootstrapTable('getData'));
    let table_data = $table.bootstrapTable('getData');
    //table_data['options'] = 'test_env';
    table_data.push({"options":ENV})
    //console.log(table_data[0]);
    console.log(table_data);
    //let json_string = JSON.stringify(table_data);
    //console.log(json_string);
     if (confirm('save all?')) {
      $.ajax({
            url: '/save_all',
            type: 'POST',
            traditional: true,
            data: JSON.stringify(table_data),
          contentType: 'application/json; charset=UTF-8',
          dataType: 'json',  //注意：这里是指希望服务端返回json格式的数据
          success: function (data) {
                if (data=="success") {
                    alert("save successful!");
                    $('#table').bootstrapTable("refresh");
                    }
                if (data=="checkpoint1") {
                    alert("checkpoint1");
                    }
            }, error: function () {
                alert("save failed!");
            }
       });
       };
      console.log("save complete!");
  }


  function deleteR() {
    var arr = arguments;//参数数组
    var data = {
    "uniqueId": arr[0],
    "options": ENV
    }
    if (confirm('是否确认删除？')) {
      $.ajax({
            url: '/delrow',
            type: 'POST',
            traditional: true,
            data: JSON.stringify(data),
          contentType: 'application/json; charset=UTF-8',
          dataType: 'json',  //注意：这里是指希望服务端返回json格式的数据
          success: function (data) {
                if (data=="success") {
                    alert("删除成功！");
                    $('#table').bootstrapTable("refresh");
                    }
                if (data=="Iamin") {
                    alert("iamin");
                    }
            }, error: function () {
                alert("删除失败！");
            }
       });
       }}
