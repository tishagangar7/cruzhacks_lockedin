


document.querySelectorAll('.button1').forEach(button => {
    button.addEventListener('click', function () {
      // Remove "pressed" class from all buttons
      document.querySelectorAll('.button1').forEach(btn => btn.classList.remove('pressed'));
  
      // Add "pressed" class to the clicked button
      this.classList.add('pressed');
    });
  });