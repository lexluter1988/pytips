function copyToClipBoard() {
  var copyText = document.getElementById("permalink").getAttribute("title");
  console.log('Text is: ', copyText)
  navigator.clipboard.writeText(copyText)
  .then(() => {
  console.log('Success');
  })
  .catch(err => {
  console.log('Something went wrong', err);
  });
}