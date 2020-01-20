 
  "use strict";
  function test_button(){
    let rowdata = JSON.stringify($table.bootstrapTable('getData')[1]);
    console.log(rowdata);
  }
    
  function save_all(){
    let table_data = JSON.stringify($table.bootstrapTable('getData'));
    console.log(table_data);
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
       }
  }


  function deleteR(id) {
    var data = {
    "rowid": id,
    "options": "delete"
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

  function addR(indexvalue){
    var arr = arguments;//参数数组
    //var nextrow = arr[0] + 1;
    var nextrow = parseInt(arr[0]) + 1;
    let rowdata = JSON.stringify($table.bootstrapTable('getData')[1]);
    //let indexvalue = indexvalue + 1; string concatenate, not integer plus
    console.log(nextrow);
    console.log(indexvalue);
    var data = {'id': '0', 'name': '0', 'price': '0','amount':'0'}; //define a new row data
    $table.bootstrapTable('insertRow', {index: nextrow,row: data})
    //$(insert());
    }  

  function insert(){
      $addbt.click(function () {
      $table.bootstrapTable('selectPage', 1); //Jump to the first page 
      var data = {'id': '0', 'name': '0', 'price': '0'}; //define a new row data
      $table.bootstrapTable('insertRow', {index: 0,row: data})
      //alert(JSON.stringify($table.bootstrapTable('getData')))
    })

      $getandsave.click(function () {
            let dataList = JSON.parse(JSON.stringify($('#table').bootstrapTable('getData')));//return all data in table
            let data = [];
            //新增数组
            let addData = [];
            for (var i = 0; i < dataList.length; i++) {
                if (dataList[i].YGFJ_ID == null) {
                    //新增数组填充
                    data.push(dataList[i]);
                }
            }
            $.ajax({
                url: '/YGJFJ/AddFj',
                type: 'post',
                traditional: true,
                dataType: 'json',
                data: { data: JSON.stringify(data), status: 'add' },
                success: function (data) {
                    if (data == "success") {
                        alert("新增成功！");
                        $('#table').bootstrapTable("refresh");
                    }
                },
                error: function () {
                    alert("新增失败！");

                }
            })
        });
    }


    function getIdSelections() {
    return $.map($table.bootstrapTable('getSelections'), function (row) {
      return row.id
    })
  }

    function responseHandler(res) {
    $.each(res.rows, function (i, row) {
      row.state = $.inArray(row.id, selections) !== -1
    })
    return res
  }

    function detailFormatter(index, row) {
    var html = []
    $.each(row, function (key, value) {
      html.push('<p><b>' + key + ':</b> ' + value + '</p>')
    })
    return html.join('')
  }

    function operateFormatter(value, row, index) {
    return [
      '<a class="like" href="javascript:void(0)" title="Like">',
      '<i class="glyphicon glyphicon-heart"></i>',
      '</a>  ',
      '<a class="remove" href="javascript:void(0)" title="Remove">',
      '<i class="glyphicon glyphicon-remove"></i>',
      '</a>'
            ].join('')
            }

    window.operateEvents = {
      'click .like': function (e, value, row, index) {
      alert('You click like action, row: ' + JSON.stringify(row))
       },
      'click .remove': function (e, value, row, index) {
      $table.bootstrapTable('remove', {
        field: 'id',
        values: [row.id]
      })
      }
      }


    function rendertable(table) {
            $table.bootstrapTable({
            url: 'static/db_records.json',  // 请求数据源的路由
            editable: true,
            reorderableRows: false,
            pagination: true, //前端处理分页
            //singleSelect: false,//是否只能单选
            search: false, //显示搜索框，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            toolbar: '#toolbar', //工具按钮用哪个容器
            striped: true, //是否显示行间隔色
            cache: false, //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            //pageNumber: 1, //初始化加载第10页，默认第一页
            showExport: true,
            pageSize: 10, //每页的记录行数（*）
            pageList: [10, 20, 50, 100], //可供选择的每页的行数（*）
            strictSearch: true,//设置为 true启用 全匹配搜索，false为模糊搜索
            showColumns: true, //显示内容列下拉框
            showRefresh: true, //显示刷新按钮
            sortable: true,
            //minimumCountColumns: 2, //当列数小于此值时，将隐藏内容列下拉框
            clickToSelect: false, //设置true， 将在点击某行时，自动勾选rediobox 和 checkbox
            //uniqueId: "id", //每一行的唯一标识，一般为主键列
            //showToggle: true, //是否显示详细视图和列表视图的切换按钮
            //cardView: false, //是否显示详细视图可以显示详细页面模式,在每行最前边显示+号#}
            //sidePagination: "server", //分页方式：client客户端分页，server服务端分页（*）
            columns: [
            {
                title: 'rowid',
                align: 'center',
                checkbox: 'false'
            }, 
            {
                field: 'IP address',
                title: 'IP address',
                align: 'center',  //对齐方式，居中
                sortable:'true',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                }
            }, 
            {
                field: 'Instance name',
                title: 'Instance name',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                }

            }, 
            {
                field: 'jdbc connecting string',
                title: 'jdbc connecting string',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                          }
            },
             {
                field: 'Oracle passwd',
                title: 'Oracle passwd',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                          }
            },
            {
                field: 'datafile',
                title: 'datafile',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                          }
            },
            {
                field: 'logfile',
                title: 'logfile',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                          }
            },
            {
                field: 'rman dump file',
                title: 'rman dump file',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                          }
            },
            {
                field: 'cron job',
                title: 'cron job',
                align: 'center',
                editable: {
                        type: 'text',
                        title: 'change content',
                        placement: 'right',
                        emptytext: "emptytext",
                          }
            },
            {
                field: "operate", 
                title: "operate", 
                width: 90, 
                formatter: function (value,row,index) {
                return '<a href="###" onclick="addR(\'' + index + '\')"><img src="static/addbutton.png" height="21" width="21"></a> &nbsp; &nbsp;<a href="###" onclick="deleteR(\'' + row.id + '\')"><img src="static/delbutton.png" height="21" width="21"></a>';}
             },
            ],
            onLoadSuccess: function(){  //加载成功时执行
                console.info("datafile load success");
                },
            onLoadError: function(){  //加载失败时执行
                console.info("datafile load failed");
                }
        });
    };