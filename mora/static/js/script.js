var commonUiElement={}
commonUiElement={
    userDate:'',
     dateElement:$(".datePicker"),
     dateInputElement:$(".date_element"),
     dateInputId:$("#dateInput"),
     searchElement:$("input#searchId"),
     init:function(){
//        commonUiElement.addMask(commonUiElement.dateInputElement, "99-99-9999") ;
         commonUiElement.addDatePicker();
         commonUiElement.searchData();
         commonUiElement.dateInputElement.keyup(function(){
             commonUiElement.userDate=$(this).val()
         })
         commonUiElement.dateInputElement.blur(function(){
             if((!commonUiElement.userDate.contains('/')) && (!commonUiElement.userDate.contains(' '))){
                 var date = Date.parse(commonUiElement.userDate);
                 if (date !== null) {
                     var convertedDate=date.toString("dd-MM-yyyy");
                     if(commonUiElement.userDate.length==6 || commonUiElement.userDate.length==8 || commonUiElement.userDate.length==10){
                         commonUiElement.dateInputElement.val(convertedDate);
                     }
                 }
             }
         });
     },
    addMask:function(element, mask){
        element.mask(mask);
    },
    addDatePicker:function(){
        commonUiElement.dateElement.datetimepicker({
            pickTime: false
        })

    },
    searchData:function(){
        commonUiElement.searchElement.keyup(function() {
                jQuery.ajax({
                    url: "/mo/search/list",
                    data: "search=" + commonUiElement.searchElement.val(),
                    success: function (data) {
                        $("#error").html(data);
                    }
             });
        });
    }
}

$(function() {

    commonUiElement.init();


});


