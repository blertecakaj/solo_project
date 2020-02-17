function countDailyCalories(){
  var arr = document.getElementsByName('daily_calories');
  var tot=0;
  for(var i=0;i<arr.length;i++){
      if(parseInt(arr[i].value))
          tot += parseInt(arr[i].value);
  }
  document.getElementById('total').value = tot;
}
